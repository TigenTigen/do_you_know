from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='layout/wrapper.html'), name='main_page'),
    path('core/', include('core.urls', namespace='core')),
    path('social/', include('social_django.urls', namespace='social')),
    path('accounts/', include('user.urls', namespace='user')),
    path('admin/', admin.site.urls),
]
