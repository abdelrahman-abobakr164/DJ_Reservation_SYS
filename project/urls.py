from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("superuser/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
