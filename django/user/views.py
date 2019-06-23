from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from user.forms import CustomUserCreationForm
from user.models import AdvUser, signer

class RegictrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('user:registration_done')

class RegictrationDoneView(TemplateView):
    template_name = 'registration/registration_done.html'

def registration_confirmation(request, sign):
    try:
        username = signer.unsign(sign)
        user = get_object_or_404(AdvUser, username=username)
        user.confirm()
        success = True
    except:
        success = False
    return render(request, 'registration/registration_confirmed.html', context={'success': success})

class ProfileView(TemplateView, LoginRequiredMixin):
    template_name = 'registration/profile.html'

class CustomLoginView(LoginView):
    #template_name = 'registration/login.html'
    #redirect_field_name = 'next'
    #extra_context = {}
    #authentication_form = django.contrib.auth.forms.AuthenticationForm
    #default_context includes parameters form, next + extra_context
    pass

class CustomLogoutView(LogoutView):
    #next_page = settings.LOGOUT_REDIRECT_URL
    #redirect_field_name = 'next'
    #template_name = 'registration/logged_out.html' # used if next_page = None
    #extra_context = {} # used if next_page = None
    #redirect_field_name = 'next'
    pass

class CustomPasswordChangeView(PasswordChangeView):
    #template_name = 'registration/password_change_form.html'
    #success_url = 'password_change_done' # path_name
    #form_class = django.contrib.auth.forms.PasswordChangeForm
    #extra_context = {}
    #default_context includes parameters form, title + extra_context
    pass

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    #template_name = 'registration/password_change_done.html'
    #extra_context = {}
    #default_context includes parameters title + extra_context
    pass

# PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetComplitView
# отвечают за сброс пароля пользовтелем через письма со специальными ссылками,
# направляемыми на электронный адрес пользователя
# данный функционал требует сложной настройки
# ДОДЕЛАТЬ!!!
