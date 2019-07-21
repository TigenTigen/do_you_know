from django.test import TestCase
from django.urls import reverse
from termcolor import colored

from core.models import Theme, Book, Movie, Person
from core.factories import ThemeFactory, BookFactory, MovieFactory, PersonFactory
from user.factories import AdvUserFactory

class UniversalValidationListViewTest(TestCase):
    model = None
    factory = None
    url = None
    login_url = None
    template_name_list = ['core/validation_list.html', 'core/validation_form.html']

    @classmethod
    def setUpTestData(cls):
        if cls.url:
            print(colored('Начинаю тестировать контроллер: {}'.format(cls.url), 'yellow'))

    @classmethod
    def tearDownClass(cls):
        if cls.url:
            print(colored('Тестирование {} окончено'.format(cls.url), 'green'))
        super().tearDownClass()

    def test_get_with_no_instances_for_unauthenticated_user(self):
        if self.model:
            self.assertEqual(self.model.objects.count(), 0)
            response = self.client.get(self.url)
            self.assertRedirects(response, self.login_url)

    def test_get_with_no_instances(self):
        if self.model:
            self.assertEqual(self.model.objects.count(), 0)
            user = AdvUserFactory()
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/validation_list.html')
            self.assertEqual(response.context['object_list'].count(), 0)
            self.assertContains(response, 'Данные отсутствуют', count = 1)

    def create_different_instances(self):
        self.factory(title = 'just_created')
        self.factory(title = 'approved_once', approve_score = 1)
        self.factory(title = 'is_validated_by_staff', is_validated_by_staff = True)
        self.factory(title = 'is_validated_by_users', is_validated_by_users = True, approve_score = 5)

    def test_get_with_different_instances(self):
        if self.model:
            self.create_different_instances()
            self.assertEqual(self.model.objects.count(), 4)
            user = AdvUserFactory()
            self.client.force_login(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            for template_name in self.template_name_list:
                self.assertTemplateUsed(response, template_name)
            object_list = response.context['object_list']
            self.assertEqual(object_list.count(), 2)
            self.assertEqual(object_list.first().approve_score, 1)
            self.assertContains(response, 'just_created', count = 1)
            self.assertContains(response, 'approved_once', count = 1)
            self.assertNotContains(response, 'is_validated_by_staff')
            self.assertNotContains(response, 'is_validated_by_users')
            self.assertInHTML('<input type="hidden" name="object_id" value="{}">'.format(object_list.first().id), response.content.decode('utf-8'), count = 1)
            self.assertInHTML('<input type="hidden" name="object_id" value="{}">'.format(object_list.last().id), response.content.decode('utf-8'), count = 1)
            self.assertInHTML('<label class="d-inline-block mr-4">Рейтинг одобрения: 1</label>', response.content.decode('utf-8'), count = 1)
            self.assertInHTML('<i class="material-icons" style="font-size: 18px;">arrow_upward</i>', response.content.decode('utf-8'), count = 2)

    def test_get_with_staff_user(self):
        if self.model:
            user = AdvUserFactory(is_staff = True)
            self.client.force_login(user)
            for i in range(10):
                if i % 2 == 0:
                    self.factory(created_by_user_id = user.id)
                else:
                    self.factory()
            self.assertEqual(self.model.objects.count(), 10)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            for template_name in self.template_name_list:
                self.assertTemplateUsed(response, template_name)
            object_list = response.context['object_list']
            self.assertEqual(object_list.count(), 10)
            for object in object_list[:5:]:
                self.assertEqual(object.user(), user)
            staff_button_html = '<button type="submit" name="staff_validation" class="btn btn-light mr-2">Отправить в основной список</button>'
            self.assertInHTML(staff_button_html, response.content.decode('utf-8'), count = 10)
            self.assertContains(response, 'arrow_upward', count = 5)

    def test_with_creator_user(self):
        if self.model:
            self.assertEqual(self.model.objects.count(), 0)
            user = AdvUserFactory()
            self.client.force_login(user)
            for i in range(10):
                if i % 3 == 0:
                    instance = self.factory(created_by_user_id = user.id)
                elif i % 3 == 1:
                    instance = self.factory(approve_score = 1)
                    instance.user_voted.add(user)
                else:
                    instance = self.factory()
            self.assertEqual(self.model.objects.count(), 10)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            for template_name in self.template_name_list:
                self.assertTemplateUsed(response, template_name)
            object_list = response.context['object_list']
            self.assertEqual(object_list.count(), 10)
            for object in object_list.reverse()[:3:]:
                self.assertIn(user, object.user_voted.all())
            staff_button_html = '<button type="submit" name="staff_validation" class="btn btn-light mr-2">Отправить в основной список</button>'
            self.assertInHTML(staff_button_html, response.content.decode('utf-8'), count = 0)
            self.assertContains(response, 'arrow_upward', count = 3)
            self.assertContains(response, 'Спасибо, что приняли участие в голосовании!', count = 3)

class TestValidationThemeListView(UniversalValidationListViewTest):
    model = Theme
    factory = ThemeFactory
    url = reverse('core:theme_list_validation')
    login_url = '/accounts/login/?next=/core/themes/validation/'

class TestValidationBookListView(UniversalValidationListViewTest):
    model = Book
    factory = BookFactory
    url = reverse('core:book_list_validation')
    login_url = '/accounts/login/?next=/core/books/validation/'

class TestValidationMovieListView(UniversalValidationListViewTest):
    model = Movie
    factory = MovieFactory
    url = reverse('core:movie_list_validation')
    login_url = '/accounts/login/?next=/core/movies/validation/'

class TestValidationPersonListView(UniversalValidationListViewTest):
    model = Person
    factory = PersonFactory
    url = reverse('core:person_list_validation')
    login_url = '/accounts/login/?next=/core/persons/validation/'

    def create_different_instances(self):
        self.factory(name = 'just_created')
        self.factory(name = 'approved_once', approve_score = 1)
        self.factory(name = 'is_validated_by_staff', is_validated_by_staff = True)
        self.factory(name = 'is_validated_by_users', is_validated_by_users = True, approve_score = 5)

class TestValidationFanctionView(TestCase):
    url = reverse('core:validation')
    model_list = ['Theme', 'Book', 'Movie', 'Person']
    factory_list = [ThemeFactory, BookFactory, MovieFactory, PersonFactory]

    @classmethod
    def setUpTestData(cls):
        print(colored('Начинаю тестировать контроллер: core:validation', 'yellow'))

    @classmethod
    def tearDownClass(cls):
        print(colored('Тестирование core:validation окончено', 'green'))
        super().tearDownClass()

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_with_authenticated_user(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_with_unauthenticated_user(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/validation/')

    def test_post_with_authenticated_user_and_no_data(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_with_no_instances(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for model_name in self.model_list:
            data = {'model': model_name, 'object_id': 1}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 404)

    def test_post_staff_validation(self):
        user = AdvUserFactory(is_staff = True)
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            data = {'model': instance.model(), 'object_id': instance.id, 'staff_validation': True}
            response = self.client.post(self.url, data)
            updated_instance = factory._meta.model.objects.get(id = instance.id)
            self.assertEqual(instance, updated_instance)
            self.assertTrue(updated_instance.is_validated_by_staff)

    def test_post_user_approve(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            data = {'model': instance.model(), 'object_id': instance.id, 'user_approve': True}
            response = self.client.post(self.url, data)
            updated_instance = factory._meta.model.objects.get(id = instance.id)
            self.assertEqual(instance, updated_instance)
            self.assertEqual(updated_instance.approve_score, 1)
            self.assertIn(user, updated_instance.user_voted.all())

    def test_post_user_disapprove(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            data = {'model': instance.model(), 'object_id': instance.id, 'user_disapprove': True}
            response = self.client.post(self.url, data)
            updated_instance = factory._meta.model.objects.get(id = instance.id)
            self.assertEqual(instance, updated_instance)
            self.assertEqual(updated_instance.approve_score, -1)
            self.assertIn(user, updated_instance.user_voted.all())

class Test_created_by_user(TestCase):
    url = reverse('core:created_by_user')
    factory_list = [ThemeFactory, BookFactory, MovieFactory, PersonFactory]

    @classmethod
    def setUpTestData(cls):
        print(colored('Начинаю тестировать контроллер: core:created_by_user', 'yellow'))

    @classmethod
    def tearDownClass(cls):
        print(colored('Тестирование core:created_by_user окончено', 'green'))
        super().tearDownClass()

    def test_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/created_by_user/')

    def test_with_no_instances(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/created_by_user.html')
        dict = response.context['created_by_user_dict']
        for key, value in dict.items():
            self.assertEqual(value.count(), 0)
        self.assertNotContains(response, '<dl class="row">')

    def test_with_themes(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for i in range(10):
            if i % 2 == 0:
                ThemeFactory(created_by_user_id = user.id)
            else:
                ThemeFactory()
        self.assertEqual(Theme.objects.count(), 10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/created_by_user.html')
        dict = response.context['created_by_user_dict']
        theme_qs = dict.pop('Темы')
        self.assertEqual(theme_qs.count(), 5)
        for theme in theme_qs:
            self.assertEqual(theme.user(), user)
        for key, value in dict.items():
            self.assertEqual(value.count(), 0)
        self.assertContains(response, '<dl class="row">', count = 1)
        self.assertContains(response, '<dt class="col-sm-4">', count = 5)

    def test_with_instances_of_all_models(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            for i in range(10):
                if i % 2 == 0:
                    factory(created_by_user_id = user.id)
                else:
                    factory()
            self.assertEqual(factory._meta.model.objects.count(), 10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/created_by_user.html')
        dict = response.context['created_by_user_dict']
        for key, value in dict.items():
            self.assertEqual(value.count(), 5)
            for instance in value:
                self.assertEqual(instance.user(), user)
        self.assertContains(response, '<dl class="row">', count = 4)
        self.assertContains(response, '<dt class="col-sm-4">', count = 20)
