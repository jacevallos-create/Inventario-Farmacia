from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve
from apps.core.views import landing

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/v1/", include("apps.core.api_urls")),
    path("app/", include("apps.core.urls")),
    path("", landing, name="home"),
]
if settings.DEBUG:
    urlpatterns += [
        path("static/frontend/<path:path>", serve, {"document_root": settings.BASE_DIR / "static" / "frontend"}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
