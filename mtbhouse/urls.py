from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

admin.site.site_title = "MT&B House"
admin.site.site_header = "MT&B House Admin"
admin.site.index_title = "Admin Panel - MT&B House"

urlpatterns = [
    # path('', lambda request: redirect('accounts/signin/', permanent=False)), # no addres redirect to signin
    path('nomanjazal/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('', include('ecom.urls')),
    path('users/client/', include('clients.urls')),
    path('users/merchant/', include('merchants.urls')),
    path('users/employee/', include('employees.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
