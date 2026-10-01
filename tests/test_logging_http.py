import io
import json
import logging
import uuid

import pytest
from django.http import JsonResponse
from django.template import Context, Template
from django.test import Client, RequestFactory, override_settings
from django.urls import path

from app.foundation.logging import SafeJsonFormatter, request_id
from app.foundation.middleware import CorrelationMiddleware
from app.foundation.views import live

CANARY = "SYNTHETIC_CANARY_PLATFORM_KEY"


@pytest.mark.parametrize("event", [CANARY, {"secret": CANARY}, [CANARY], None])
def test_all_log_message_exception_and_metadata_sinks_scrubbed(event):
    record = logging.LogRecord("openai.http", logging.ERROR, CANARY, 1, CANARY, (), None)
    record.event = event
    record.authorization = CANARY
    record.url = f"https://example.com/?key={CANARY}"
    record.request_id = CANARY
    record.run_id = str(uuid.uuid4())
    record.exc_text = f"Traceback {CANARY}"
    record.stack_info = CANARY
    result = SafeJsonFormatter().format(record)
    assert CANARY not in result
    assert len(result.encode()) < 1024
    payload = json.loads(result)
    assert payload["error"] == "exception_suppressed"
    assert "request_id" not in payload
    assert payload["run_id"] == record.run_id


def test_raw_exception_repr_is_never_formatted():
    class UnsafeError(Exception):
        def __str__(self):
            raise AssertionError("exception string must not be evaluated")

    error = UnsafeError(CANARY)
    record = logging.LogRecord(
        "aap", logging.ERROR, "", 1, error, (CANARY,), (UnsafeError, error, None)
    )
    assert CANARY not in SafeJsonFormatter().format(record)


def test_request_id_ignores_caller_and_resets_context():
    request = RequestFactory().get("/health/live", HTTP_X_REQUEST_ID=CANARY)
    response = CorrelationMiddleware(live)(request)
    assert str(uuid.UUID(response["X-Request-ID"])) == response["X-Request-ID"]
    assert response["X-Request-ID"] != CANARY
    assert request_id.get() is None


def test_context_cleared_on_exception():
    def explode(request):
        raise RuntimeError(CANARY)

    with pytest.raises(RuntimeError):
        CorrelationMiddleware(explode)(RequestFactory().get("/"))
    assert request_id.get() is None


def test_live_does_not_probe_db_or_provider(client):
    assert client.get("/health/live").json() == {"status": "alive"}


def test_unavailable_db_readiness_is_generic(client):
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "execution_ready": False}


def test_browser_headers_and_no_admin(client):
    response = client.get("/health/live")
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]
    assert "script-src 'none'" in response["Content-Security-Policy"]
    assert response["X-Frame-Options"] == "DENY"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["Referrer-Policy"] == "no-referrer"
    assert client.get("/admin/").status_code == 404


def test_escaping_default_is_preserved():
    text = '<script src="https://example.com">SYNTHETIC_CANARY</script>'
    rendered = Template("{{ content }}").render(Context({"content": text}))
    assert "<script" not in rendered
    assert "&lt;script" in rendered


def crash(request):
    raise RuntimeError(CANARY)


def mutate(request):
    return JsonResponse({"synthetic": True})


urlpatterns = [path("crash", crash), path("mutate", mutate)]
handler500 = "app.foundation.views.server_error"
handler403 = "app.foundation.views.permission_denied"


@override_settings(ROOT_URLCONF=__name__)
def test_error_response_and_real_logging_do_not_expose_canary():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SafeJsonFormatter())
    logger = logging.getLogger("django.request")
    logger.addHandler(handler)
    try:
        client = Client(raise_request_exception=False)
        response = client.get(f"/crash?secret={CANARY}", HTTP_AUTHORIZATION=CANARY)
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "http_500"
        assert CANARY not in response.content.decode() + stream.getvalue()
        assert "exception_suppressed" in stream.getvalue()
    finally:
        logger.removeHandler(handler)


@override_settings(ROOT_URLCONF=__name__)
def test_csrf_cookie_mutation_is_denied():
    response = Client(enforce_csrf_checks=True).post("/mutate", {"key": CANARY})
    assert response.status_code == 403
    assert CANARY not in response.content.decode()
