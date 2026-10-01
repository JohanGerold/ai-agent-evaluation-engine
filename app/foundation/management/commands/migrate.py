"""Foundation migration credential and timeout convention, not role bootstrap."""

import logging

from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.migrate import Command as DjangoMigrate

from app.foundation.safety import validate_database


class Command(DjangoMigrate):
    def handle(self, *args, **options):
        if settings.AAP_ENTRYPOINT != "migration":
            raise CommandError("migration_entrypoint_required")
        validate_database(migration=True, require_baseline=False)
        result = super().handle(*args, **options)
        logging.getLogger("aap.migration").info("", extra={"event": "migration_ok"})
        return result
