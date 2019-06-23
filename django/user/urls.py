from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from user.views import *

# comon_prefix: accounts/'
app_name = 'user'
urlpatterns = [
    # pure default paths:
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    # custom paths:
    path('registration/', RegictrationView.as_view(), name='registration'),
]
