from django.contrib import admin
from django.urls import path, include
from utils import error_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('product.urls')),
    path('api/', include('account.urls')),
]

handler404 = 'utils.error_views.handler404'
handler500 = 'utils.error_views.handler500'