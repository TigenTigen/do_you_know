from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from termcolor import colored
from random import randint, choice

from core.models import Theme, Book, Cycle, Movie, Person, Role
from core.forms import ThemeAutoLookupForm, BookAutoLookupForm, MovieAutoLookupForm, PersonForm
from core.factories import ThemeFactory, BookFactory, MovieFactory, PersonFactory
from user.factories import AdvUserFactory

class UniversalCreateViewTest(TestCase):
    url = None
    view_name = None
    login_redirect_url = None
    form_class = None
    model = None
    extra_context_list = None
    invalid_data_dict = None
    context_form_name = 'form'

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
            form = response.context[self.context_form_name]
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
            form = response.context[self.context_form_name]
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
            form = response.context[self.context_form_name]
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
        if response.status_code == 200:
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

class Test_person_create(UniversalCreateViewTest):
    view_name = 'person_create'
    form_class = PersonForm
    model = Person
    extra_context_list = ['image_form']
    invalid_data_dict = {'name': '   ', 'description': 'some_text'}
    related_name_choices = ['creator', 'author', 'character', 'director', 'writer']
    model_dict = {'creator': Theme, 'author': Book, 'character': Book, 'director': Movie, 'writer': Movie}

    @classmethod
    def get_url(cls):
        random_related_name = choice(cls.related_name_choices)
        related_model = cls.model_dict[random_related_name]
        superinstance = related_model.objects.create(title = 'some title for related_instance')
        url = reverse('core:person_create', args = [random_related_name, superinstance.pk])
        print(colored('Random url for basic tests: {}'.format(url), 'yellow'))
        cls.login_redirect_url = '/accounts/login/?next=/core/persons/create/{}/{}/'.format(random_related_name, superinstance.pk)
        return url

    def make_post_response_with_valid_data(self, url, extra_data_dict = {}):
        self.assertEqual(self.model.objects.count(), 0)
        user = AdvUserFactory()
        self.client.force_login(user)
        valid_data_dict = {'name': 'test_name', 'description': 'some_text', 'created_by_user_id': user.id}
        valid_data_dict.update(extra_data_dict)
        response = self.client.post(url, valid_data_dict)
        if response.status_code == 200:
            self.print_invalid_form_errors(response.context['form'])
        self.assertEqual(self.model.objects.count(), 1)
        created_instance = self.model.objects.get()
        self.assertEqual(created_instance.name, 'test_name')
        self.assertEqual(created_instance.description, 'some_text')
        self.assertIsNone(created_instance.born)
        self.assertRedirects(response, created_instance.get_absolute_url())

    def test_post_creator(self):
        theme = ThemeFactory()
        url = reverse('core:person_create', kwargs = {'related_name': 'creator', 'pk':theme.pk})
        self.make_post_response_with_valid_data(url)
        self.assertEqual(theme.creators.count(), 1)

    def test_post_author(self):
        book = BookFactory()
        url = reverse('core:person_create', kwargs = {'related_name': 'author', 'pk':book.pk})
        self.make_post_response_with_valid_data(url)
        book = Book.objects.get(id = book.id)
        self.assertIsNotNone(book.author)

    def test_post_character(self):
        book = BookFactory()
        url = reverse('core:person_create', kwargs = {'related_name': 'character', 'pk':book.pk})
        self.make_post_response_with_valid_data(url)
        self.assertEqual(book.characters.count(), 1)

    def test_post_director(self):
        movie = MovieFactory()
        url = reverse('core:person_create', kwargs = {'related_name': 'director', 'pk':movie.pk})
        self.make_post_response_with_valid_data(url)
        movie = Movie.objects.get(id = movie.id)
        self.assertIsNotNone(movie.director)

    def test_post_writer(self):
        movie = MovieFactory()
        url = reverse('core:person_create', kwargs = {'related_name': 'writer', 'pk':movie.pk})
        self.make_post_response_with_valid_data(url)
        movie = Movie.objects.get(id = movie.id)
        self.assertIsNotNone(movie.writer)

    def make_post_response_with_valid_data_with_existing_person(self, url, extra_data_dict = {}):
        self.assertEqual(self.model.objects.count(), 0)
        user = AdvUserFactory()
        self.client.force_login(user)
        person = PersonFactory()
        valid_data_dict = {'name': person.name, 'created_by_user_id': user.id}
        valid_data_dict.update(extra_data_dict)
        response = self.client.post(url, valid_data_dict)
        if response.status_code == 200:
            self.print_invalid_form_errors(response.context['form'])
        self.assertEqual(self.model.objects.count(), 1)
        created_instance = self.model.objects.get()
        self.assertEqual(created_instance.name, person.name)
        self.assertIsNone(created_instance.born)
        self.assertRedirects(response, created_instance.get_absolute_url())

    def test_post_creator_with_existing_person(self):
        theme = ThemeFactory()
        url = reverse('core:person_create', args = ['creator', theme.pk])
        self.make_post_response_with_valid_data_with_existing_person(url)
        self.assertEqual(theme.creators.count(), 1)

    def test_post_author_with_existing_person(self):
        book = BookFactory()
        url = reverse('core:person_create', args = ['author', book.pk])
        self.make_post_response_with_valid_data_with_existing_person(url)
        book = Book.objects.get(id = book.id)
        self.assertIsNotNone(book.author)

    def test_post_character_with_existing_person(self):
        book = BookFactory()
        url = reverse('core:person_create', args = ['character', book.pk])
        self.make_post_response_with_valid_data_with_existing_person(url)
        self.assertEqual(book.characters.count(), 1)

    def test_post_director_with_existing_person(self):
        movie = MovieFactory()
        url = reverse('core:person_create', args = ['director', movie.pk])
        self.make_post_response_with_valid_data_with_existing_person(url)
        movie = Movie.objects.get(id = movie.id)
        self.assertIsNotNone(movie.director)

    def test_post_writer_with_existing_person(self):
        movie = MovieFactory()
        url = reverse('core:person_create', args = ['writer', movie.pk])
        self.make_post_response_with_valid_data_with_existing_person(url)
        movie = Movie.objects.get(id = movie.id)
        self.assertIsNotNone(movie.writer)

class Test_person_create_as_role(UniversalCreateViewTest):
    view_name = 'person_create_as_role'
    form_class = PersonForm
    model = Person
    context_form_name = 'character_form'
    extra_context_list = ['actor_name_field']
    invalid_data_dict = {'name': '   ', 'description': 'some_text'}

    @classmethod
    def get_url(cls):
        cls.movie = MovieFactory()
        cls.login_redirect_url = '/accounts/login/?next=/core/persons/role/create/{}/'.format(cls.movie.pk)
        return reverse('core:person_create_as_role', args = [cls.movie.pk])

    def make_post_response_with_valid_data(self, extra_data_dict = {}):
        user = AdvUserFactory()
        self.client.force_login(user)
        valid_data_dict = {'name': 'test_name', 'description': 'some_text', 'actor_name': 'test_actor_name', 'created_by_user_id': user.id}
        valid_data_dict.update(extra_data_dict)
        response = self.client.post(self.url, valid_data_dict)
        if response.status_code == 200:
            self.print_invalid_form_errors(response.context['form'])
        self.assertEqual(Role.objects.count(), 1)
        new_role = Role.objects.get()
        self.assertEqual(new_role.character.name, valid_data_dict['name'])
        self.assertEqual(new_role.character.description, valid_data_dict['description'])
        self.assertEqual(new_role.actor.name, valid_data_dict['actor_name'])
        self.assertRedirects(response, self.movie.get_absolute_url())

    def test_post_with_new_character(self):
        self.make_post_response_with_valid_data()

    def test_post_with_existing_character(self):
        person = PersonFactory(name = 'existing fictional character', is_fictional = True)
        extra_data_dict = {'name': person.name, 'description': None}
        self.make_post_response_with_valid_data(extra_data_dict)

    def test_post_with_existing_actor(self):
        person = PersonFactory(name = 'existing fictional character', is_fictional = True)
        extra_data_dict = {'actor_name': person.name}
        self.make_post_response_with_valid_data(extra_data_dict)
