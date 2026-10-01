from django.core.checks import Error, Tags, register

from app.foundation.safety import configuration_errors


@register(Tags.security)
def foundation_checks(app_configs, **kwargs):
    return [Error(reason, id="aap.E001") for reason in configuration_errors()]
