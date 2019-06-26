from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='layout/wrapper.html'), name='main_page'),
    path('core/', include('core.urls', namespace='core')),
    path('social/', include('social_django.urls', namespace='social')),
    path('accounts/', include('user.urls', namespace='user')),
    path('admin/', admin.site.urls),
    path('selectable/', include('selectable.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
