import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
application = get_wsgi_application()

from app.foundation.safety import startup  # noqa: E402

startup()
