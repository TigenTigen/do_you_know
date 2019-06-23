from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('user.urls')),
    path('admin/', admin.site.urls),
]
