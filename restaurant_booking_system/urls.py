from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Include API URLs
    path('', include('core.urls')),     # Include UI URLs
]
