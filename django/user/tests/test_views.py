from django.test import TestCase
from django.urls import reverse
from user.forms import CustomUserCreationForm
from user.models import AdvUser, signer
from user.factories import AdvUserFactory
from contacts.models import Category

class TestViews_for_unauthenticated_user(TestCase):
    def RegistrationView_generated_form_test(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/registration_form.html')
        self.assertIsNotNone(response.context['form'])
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        for field_name in CustomUserCreationForm.Meta.fields:
            self.assertContains(response, 'id="id_{}"'.format(field_name), count=1)
        self.assertContains(response, '<button type="submit" class="btn btn-success">Сохранить</button>', count=1)

    def test_RegictrationView_GET(self):
        response = self.client.get(reverse('user:registration'))
        self.RegistrationView_generated_form_test(response)

    def test_RegictrationView_POST_with_no_data(self):
        response = self.client.post(reverse('user:registration'))
        self.RegistrationView_generated_form_test(response)
        self.assertIsNotNone(response.context['form'].non_field_errors())
        for field in response.context['form']:
            self.assertIsNotNone(field.errors)

    def test_RegictrationView_POST_with_correct_data(self):
        data_dict = {
            'username': 'test_user',
            'password1': 'test_password',
            'password2': 'test_password',
            'email': 'test_email@email.com'
        }
        response = self.client.post(reverse('user:registration'), data_dict)
        self.assertRedirects(response, reverse('user:registration_done'))
        self.assertEqual(AdvUser.objects.count(), 1)

    def RegictrationDoneView(self):
        response = self.client.get(reverse('user:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/registration_done.html')

    def test_registration_confirmation_with_incorrect_data(self):
        response = self.client.get(reverse('user:registration_confirmed', args=['some_string']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/registration_confirmed.html')
        self.assertIn('success', response.context)
        self.assertContains(response, '<p>В ходе регистрации пользователя, произошел сбой.</p>', count=1)
        self.assertContains(response, reverse('user:registration'), count=2)
        self.assertNotContains(response, '<p>Регистрация подтверждена.</p>')

    def test_registration_confirmation_with_correct_data(self):
        user = AdvUserFactory(is_active=False)
        self.assertFalse(user.is_active)
        sign = signer.sign(user.username)
        response = self.client.get(reverse('user:registration_confirmed', args=[sign]))
        updated_user = AdvUser.objects.get(id=user.id)
        self.assertEqual(updated_user, user)
        self.assertTrue(updated_user.is_active)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/registration_confirmed.html')
        self.assertIn('success', response.context)
        self.assertNotContains(response, '<p>В ходе регистрации пользователя, произошел сбой.</p>')
        self.assertContains(response, '<p>Регистрация подтверждена.</p>', count=1)
        self.assertContains(response, reverse('user:login'), count=2)

    def test_ProfileView(self):
        response = self.client.get(reverse('user:profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')

    def CustomPasswordResetView_generated_form_test(self, response):
        email_input_html = '<input type="email" name="email"'
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/password_reset_form.html')
        self.assertIsNotNone(response.context['form'])
        self.assertContains(response, email_input_html, count=1)

    def test_CustomPasswordResetView_GET(self):
        response = self.client.get(reverse('user:password_reset'))
        self.CustomPasswordResetView_generated_form_test(response)

    def test_CustomPasswordResetView_POST_with_no_data(self):
        response = self.client.post(reverse('user:password_reset'))
        self.CustomPasswordResetView_generated_form_test(response)
        self.assertIsNotNone(response.context['form'].non_field_errors())
        for field in response.context['form']:
            self.assertIsNotNone(field.errors)

    def test_CustomPasswordResetView_POST_with_incorrect_data(self):
        response = self.client.post(reverse('user:password_reset'), {'email': 3})
        self.CustomPasswordResetView_generated_form_test(response)
        self.assertIsNotNone(response.context['form'].non_field_errors())
        for field in response.context['form']:
            self.assertIsNotNone(field.errors)

    def test_CustomPasswordResetView_POST_with_correct_data(self):
        response = self.client.post(reverse('user:password_reset'), {'email': 'some@email.com'})
        self.assertRedirects(response, '/accounts/password_reset/done/')

    def test_CustomPasswordResetConfirmView_GET_with_invalid_link(self):
        response = self.client.get(reverse('user:password_reset_confirm', args=['some_string', 'some_string']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/password_reset_confirm.html')
        self.assertIsNone(response.context['form'])
        self.assertContains(response, '<p>В ходе сброса пароля, произошел сбой.</p>', count=1)
        self.assertContains(response, reverse('user:password_reset'), count=1)

class TestViews_for_authenticated_user(TestCase):
    def setUp(self):
        self.user = AdvUserFactory()
        self.client.force_login(self.user)

    def test_RegictrationView(self):
        response = self.client.get(reverse('user:registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/registration_form.html')
        self.assertIsNotNone(response.context['form'])
        self.assertContains(response, '<p>Вы уже выполнили регистрацию.</p>', count=1)

    def test_ProfileView(self):
        category = Category.objects.create(title='new_category')
        message = self.user.messages.create(title='some_title', text='some_text', category=category)
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/profile.html')
        self.assertContains(response, reverse('user:password_change'), count=1)
        self.assertContains(response, '<p class="m-0">Имя пользователя: {}</p>'.format(self.user.username), count=1)
        self.assertContains(response, 'some_title', count=1)
        self.assertContains(response, 'Добро пожаловать, {}'.format(self.user.username), count=1)

    def test_CustomPasswordResetView(self):
        response = self.client.get(reverse('user:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('registration/password_reset_form.html')
        self.assertIsNotNone(response.context['form'])
        self.assertContains(response, '<p>Вы уже выполнили вход.</p>', count=1)
