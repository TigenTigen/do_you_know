from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('social/', include('social_django.urls', namespace='social')),
    path('accounts/', include('user.urls', namespace='user')),
    path('admin/', admin.site.urls),
]
