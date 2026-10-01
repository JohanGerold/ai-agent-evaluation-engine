"""Reserved worker entry point; refuses task execution until later task machinery exists."""

import logging
import os

import django
from django.db import connections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
os.environ["AAP_ENTRYPOINT"] = "worker"
django.setup()

from app.foundation.safety import startup  # noqa: E402

try:
    startup()
    logging.getLogger("aap.worker").error("", extra={"event": "worker_unavailable"})
finally:
    connections.close_all()
    for connection in connections.all():
        connection.close_pool()
raise SystemExit(2)
