from django.http import JsonResponse
from django.views.decorators.http import require_GET

from app.foundation.safety import validate_database


@require_GET
def live(request):
    return JsonResponse({"status": "alive"})


@require_GET
def ready(request):
    try:
        validate_database()
    except Exception:
        return JsonResponse({"status": "unavailable", "execution_ready": False}, status=503)
    # No provider probing and no worker-readiness claim before T-020b/T-037.
    return JsonResponse({"status": "foundation_ready", "execution_ready": False})


def safe_error(request, exception=None, *, status=500):
    return JsonResponse(
        {
            "error": {"code": f"http_{status}", "message": "Request unavailable"},
            "request_id": getattr(request, "request_id", None),
        },
        status=status,
    )


def bad_request(request, exception):
    return safe_error(request, status=400)


def permission_denied(request, exception):
    return safe_error(request, status=403)


def not_found(request, exception):
    return safe_error(request, status=404)


def server_error(request):
    return safe_error(request, status=500)
