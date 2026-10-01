import logging
import time
import uuid

from app.foundation.logging import request_id

logger = logging.getLogger("aap.http")


class CorrelationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Caller headers are untrusted; create a platform-owned identifier.
        request.request_id = str(uuid.uuid4())
        token = request_id.set(request.request_id)
        start = time.monotonic()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request.request_id
            logger.info(
                "",
                extra={
                    "event": "request_complete",
                    "status": response.status_code,
                    "elapsed_ms": (time.monotonic() - start) * 1000,
                },
            )
            return response
        finally:
            request_id.reset(token)


class BrowserSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = (
            "default-src 'self'; connect-src 'self'; img-src 'self'; "
            "script-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "no-referrer"
        return response
