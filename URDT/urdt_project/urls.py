from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # ✅ Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('urdt_app.urls')),  # ✅ Include app-specific routes
]

# ✅ Ensure media files are served during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
