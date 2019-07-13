from config.universal_tests import UniversalFormTest
from user.forms import CustomUserCreationForm, UserCreationForm
from user.models import AdvUser

class TestForm(UniversalFormTest):
    form_class = CustomUserCreationForm
    form_super_class = UserCreationForm
    form_model_class = AdvUser
    all_fields_are_required = True

    def get_valid_data_dict(self):
        data_dict = {
            'username': 'test_user',
            'password1': 'test_password',
            'password2': 'test_password',
            'email': 'test_email@email.com'
        }
        return data_dict

    def get_field_validation_check_dict(self):
        field_validation_check_dict = {
            'email': [None, '', 1, 'some_string', 'some string', 'some@email@com', 'some@email', 'some@email.com'],
            'username': [None, '', 1, 'some_username', 'some username'],
        }
        return field_validation_check_dict

    def test_email(self):
        generated_email_field = self.form.fields['email']
        self.assertIsNotNone(generated_email_field)
        self.assertTrue(generated_email_field.required)
        self.assertEqual(generated_email_field.label, 'Адрес электронной почты')

    def test_save_method(self):
        data_dict = {
            'username': 'test_user',
            'password1': 'test_password',
            'password2': 'test_password',
            'email': 'test_email@email.com'
        }
        form = CustomUserCreationForm(data_dict)
        if form.is_valid():
            user = form.save()
            self.assertIsNotNone(user.email)
            self.assertFalse(user.is_active)
