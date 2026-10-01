from django.apps import AppConfig


class FoundationConfig(AppConfig):
    name = "app.foundation"

    def ready(self):
        from app.foundation import checks  # noqa: F401
        from app.foundation.safety import validate_configuration

        validate_configuration()
