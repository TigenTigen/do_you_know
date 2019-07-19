from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from termcolor import colored
from random import randint

from core.models import Theme, Book, Cycle, Movie
from core.forms import ThemeAutoLookupForm, BookAutoLookupForm, MovieAutoLookupForm
from core.factories import ThemeFactory
from user.factories import AdvUserFactory

class UniversalCreateViewTest(TestCase):
    url = None
    view_name = None
    login_redirect_url = None
    form_class = None
    model = None
    extra_context_list = None
    invalid_data_dict = None

    @classmethod
    def setUpTestData(cls):
        if cls.view_name:
            print(colored('Начинаю тестировать контроллер-класс: {}'.format(cls.view_name), 'yellow'))
            cls.url = cls.get_url()

    @classmethod
    def get_url(cls):
        return cls.url

    @classmethod
    def tearDownClass(cls):
        if cls.view_name:
            print(colored('Тестирование {} окончено'.format(cls.view_name), 'green'))
        super().tearDownClass()

    def green(self, message):
        print(colored(message, 'green'))

    def red(self, message):
        print(colored(message, 'red'))

    def print_invalid_form_errors(self, form):
        self.red('   !!!   INVALID FORM   !!!   ')
        if form.non_field_errors():
            print('   !!! form is invalid:  ', form.non_field_errors())
        for field in form:
            if field.errors:
                print('   !!! invalid field value: ', field.name, field.errors)

    def check_errors_in_content(self, response, form):
        for error in form.non_field_errors():
            self.assertInHTML(error, response.content.decode('utf-8'), count = 1)
        for field in form:
            if str(field).count('hidden') == 0:
                for error in field.errors:
                    self.assertInHTML(error, response.content.decode('utf-8'), count = 1)

    def test_get_with_unauthenticated_user(self):
        if self.login_redirect_url:
            response = self.client.get(self.url)
            self.assertRedirects(response, self.login_redirect_url)

    def test_get(self):
        if self.form_class:
            user = AdvUserFactory()
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertIsNotNone(form)
            self.assertIsInstance(form, self.form_class)
            self.assertEqual(form.initial['created_by_user_id'], user.id)
            for item in self.extra_context_list:
                self.assertIsNotNone(response.context[item])
            self.assertEqual(self.model.objects.count(), 0)

    def test_post_with_no_data(self):
        if self.form_class:
            user = AdvUserFactory()
            self.client.force_login(user)
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 200)
            form = response.context.get('form')
            self.assertIsNotNone(form)
            self.assertIsInstance(form, self.form_class)
            self.assertFalse(form.is_valid())
            self.check_errors_in_content(response, form)
            self.assertEqual(self.model.objects.count(), 0)

    def test_post_with_invalid_data(self):
        if self.invalid_data_dict:
            user = AdvUserFactory()
            self.client.force_login(user)
            response = self.client.post(self.url, self.invalid_data_dict)
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertIsNotNone(form)
            self.assertIsInstance(form, self.form_class)
            self.assertFalse(form.is_valid())
            self.check_errors_in_content(response, form)
            self.assertEqual(self.model.objects.count(), 0)

class Test_theme_create(UniversalCreateViewTest):
    url = reverse('core:theme_create')
    view_name = 'theme_create'
    login_redirect_url = '/accounts/login/?next=/core/themes/create/'
    form_class = ThemeAutoLookupForm
    model = Theme
    extra_context_list = ['image_form']
    invalid_data_dict = {'title': '   ', 'description': 'some_text'}

    def test_post_with_correct_data(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        data = {'title': 'test_title', 'description': 'some_text', 'created_by_user_id': user.id}
        response = self.client.post(self.url, data)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertRedirects(response, self.model.objects.get().get_absolute_url())

class Test_book_create(UniversalCreateViewTest):
    view_name = 'book_create'
    form_class = BookAutoLookupForm
    model = Book
    extra_context_list = ['image_form', 'cycles']
    invalid_data_dict = {'title': '   ', 'description': 'some_text'}

    @classmethod
    def get_url(cls):
        cls.theme = ThemeFactory(is_validated_by_staff = True)
        cls.cycle = cls.theme.cycles.create(title = 'cycle_title')
        cls.login_redirect_url = '/accounts/login/?next=/core/books/create/{}/'.format(cls.theme.pk)
        return reverse('core:book_create', args = [cls.theme.pk])

    def make_post_response_with_valid_data(self, extra_data_dict = {}):
        self.assertEqual(self.model.objects.count(), 0)
        user = AdvUserFactory()
        self.client.force_login(user)
        valid_data_dict = {'title': 'test_title', 'description': 'some_text', 'created_by_user_id': user.id, 'year': randint(1, 3000)}
        valid_data_dict.update(extra_data_dict)
        response = self.client.post(self.url, valid_data_dict)
        if not extra_data_dict:
            print(self.url, valid_data_dict, user, user.id)
            print(response.status_code, self.model, Movie.objects.all(), Book.objects.all())
            if response.status_code == 200:
                print(response.content.decode('utf-8'))
                self.print_invalid_form_errors(response.context['form'])
        self.assertEqual(self.model.objects.count(), 1)
        created_instance = self.model.objects.get()
        self.assertEqual(created_instance.title, 'test_title')
        self.assertIsNone(created_instance.genre)
        self.assertRedirects(response, created_instance.get_absolute_url())

    def test_post_with_correct_data(self):
        self.make_post_response_with_valid_data()
        created_instance = self.model.objects.get()
        self.assertIsNone(created_instance.genre)

    def test_post_with_correct_data_and_cycles(self):
        extra_data_dict = {'cycle': str(self.cycle.pk), 'number': '12'}
        self.make_post_response_with_valid_data(extra_data_dict)
        created_instance = self.model.objects.get()
        self.assertEqual(created_instance.number_set.count(), 1)
        self.assertEqual(created_instance.number_set.get().cycle, self.cycle)
        self.assertEqual(created_instance.number_set.get().number, 12)

    def test_post_with_correct_data_and_creating_new_cycle(self):
        extra_data_dict = {'new_cycle_title': 'new_test_cycle_title', 'number': '3'}
        self.make_post_response_with_valid_data(extra_data_dict)
        created_instance = self.model.objects.get()
        self.assertEqual(created_instance.number_set.count(), 1)
        self.assertEqual(created_instance.number_set.get().cycle.title, 'new_test_cycle_title')
        self.assertEqual(created_instance.number_set.get().number, 3)

class Test_movie_create(Test_book_create):
    view_name = 'movie_create'
    form_class = MovieAutoLookupForm
    model = Movie

    @classmethod
    def get_url(cls):
        cls.theme = ThemeFactory(is_validated_by_staff = True)
        cls.cycle = cls.theme.cycles.create(title = 'cycle_title')
        cls.login_redirect_url = '/accounts/login/?next=/core/movies/create/{}/'.format(cls.theme.pk)
        return reverse('core:movie_create', args = [cls.theme.pk])

    def test_post_with_correct_data(self):
        self.make_post_response_with_valid_data()
