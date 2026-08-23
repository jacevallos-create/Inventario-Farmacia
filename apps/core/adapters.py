import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


logger = logging.getLogger("apps.oauth")


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Report OAuth failures to Render logs without logging tokens or secrets."""

    def on_authentication_error(
        self,
        request,
        provider,
        error=None,
        exception=None,
        extra_context=None,
    ):
        logger.error(
            "Google OAuth failed: provider=%s error=%s exception_type=%s detail=%s",
            provider.id,
            error,
            type(exception).__name__ if exception else "None",
            str(exception)[:500] if exception else "No exception detail",
        )
        return super().on_authentication_error(
            request,
            provider,
            error=error,
            exception=exception,
            extra_context=extra_context,
        )
