import os
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class PolarisConfig(AppConfig):
    name = "polaris"
    verbose_name = "Django Polaris"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        """
        Initialize the app
        """
        from polaris import settings  # loads internal settings
        from polaris import cors  # loads CORS signals
        from polaris.sep24.utils import check_sep24_config

        self.check_middleware()
        self.check_protocol()
        self.check_sep23_supported()
        if "sep-24" in settings.ACTIVE_SEPS:
            check_sep24_config()

    @staticmethod
    def check_middleware():
        from django.conf import settings as django_settings

        cors_middleware_path = "corsheaders.middleware.CorsMiddleware"
        if cors_middleware_path not in django_settings.MIDDLEWARE:
            raise ImproperlyConfigured(
                f"{cors_middleware_path} is not installed in settings.MIDDLEWARE"
            )

    @staticmethod
    def check_protocol():
        from polaris import settings
        from polaris.utils import getLogger
        from django.conf import settings as django_settings

        logger = getLogger(__name__)
        if getattr(django_settings, "SECURE_PROXY_SSL_HEADER"):
            logger.debug(
                "SECURE_PROXY_SSL_HEADER should only be set if Polaris is "
                "running behind an HTTPS reverse proxy."
            )
        elif not (
            settings.LOCAL_MODE or getattr(django_settings, "SECURE_SSL_REDIRECT")
        ):
            logger.debug(
                "SECURE_SSL_REDIRECT is required to redirect HTTP traffic to HTTPS"
            )

    @staticmethod
    def check_sep23_supported():
        # use the same string comparisons as the SDK:
        # https://github.com/StellarCN/py-stellar-base/blob/master/stellar_sdk/muxed_account.py#L15
        if os.getenv("ENABLE_SEP_0023", "").lower() not in ("true", "1", "t"):
            raise ImproperlyConfigured(
                "environment variable ENABLE_SEP_0023 must be set to 'true'"
            )
