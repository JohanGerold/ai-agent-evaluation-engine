import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from app.foundation.safety import startup


class Command(BaseCommand):
    help = "Verify offline foundation configuration and actual PostgreSQL runtime role."

    def handle(self, *args, **options):
        try:
            startup()
        except Exception:
            logging.getLogger("aap.startup").error(
                "", extra={"event": "startup_refused"}, exc_info=True
            )
            raise CommandError("foundation_startup_refused") from None
        finally:
            connections.close_all()
            for connection in connections.all():
                connection.close_pool()
        logging.getLogger("aap.startup").info("", extra={"event": "startup_ok"})
