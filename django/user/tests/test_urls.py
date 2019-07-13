from config.universal_tests import UniversalURLtest
from user.urls import urlpatterns

class TestURLs(UniversalURLtest):
    app_name = 'user'
    namespace = 'user'
    urlpatterns = urlpatterns
