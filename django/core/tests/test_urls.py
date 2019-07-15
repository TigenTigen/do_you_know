from config.universal_tests import UniversalURLtest
from core.urls import urlpatterns

class TestURLs(UniversalURLtest):
    app_name = 'core'
    namespace = 'core'
    urlpatterns = urlpatterns
