"""
Django Main URL Configuration
Root URL dispatcher for the banking platform
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    
    # API Routes
    path('api/', include('accounts.urls', namespace='accounts-api')),
    
    # Health check
    path('health/', lambda request: __import__('django.http').http.JsonResponse({'status': 'healthy'}), name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
