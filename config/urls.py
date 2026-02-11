# /config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
from core.views import error_403 # Importamos tu vista de error personalizada



urlpatterns = [
    #Django Admin OK
    path('admin/', admin.site.urls),
    
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', include('core.urls')),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler403 = 'core.views.error_403'