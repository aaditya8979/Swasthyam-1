"""
URL configuration for Swasthyam project.
Routes are organized by app with i18n support.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Non-translated URLs (landing page, API endpoints)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
]

# Translated URLs (all user-facing pages)
urlpatterns += i18n_patterns(
    path('', include('main.urls')),
    path('users/', include('users.urls')),
    path('maternal/', include('maternal_health.urls')),
    path('forum/', include('community_forum.urls')),
    path('child/', include('child_tracker.urls')),
    path('calculators/', include('health_calculators.urls')),
    prefix_default_language=False,  # Don't add /en/ prefix for English
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Custom error handlers
handler404 = 'main.views.error_404'
handler500 = 'main.views.error_500'

# Admin customization
admin.site.site_header = "Swasthyam Administration"
admin.site.site_title = "Swasthyam Admin"
admin.site.index_title = "Health Data Management"



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
