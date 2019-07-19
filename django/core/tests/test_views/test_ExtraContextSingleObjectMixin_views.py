from django.test import TestCase
from django.urls import reverse

from termcolor import colored

from core.models import Theme, Person, Book, Movie
from core.views import ThemeDetail, PersonDetail, BookDetail, MovieDetail
from core.factories import QuestionFactory, ThemeFactory, PersonFactory, BookFactory, MovieFactory
from user.factories import AdvUserFactory

class UniversalDetailViewTest(TestCase):
    view = None
    model = None
    factory = None
    url_name = None

    @classmethod
    def setUpTestData(cls):
        if cls.view:
            print(colored('Начинаю тестировать контроллер-класс: {}'.format(cls.view), 'yellow'))

    @classmethod
    def tearDownClass(cls):
        if cls.view:
            print(colored('Тестирование {} окончено'.format(cls.view), 'green'))
        super().tearDownClass()

    def test_class(self):
        if self.view:
            self.assertCountEqual(self.view.queryset, self.model.objects.all_with_perfetch())

    def test_with_no_instances(self):
        if self.view:
            url = reverse('core:' + self.url_name, args = [1])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def check_templates(self, response, instance):
        template_list = ['core/common_detail.html', 'core/{}.html'.format(self.url_name), 'img/cover_lg.html']
        if instance.is_validated():
            template_list.append('questions/question_form_block.html')
            template_list.append('img/image_upload_form.html')
            if instance.images.exists():
                template_list.append('img/img_preview_set.html')
        else:
            template_list.append('core/validation_form.html')
        for template in template_list:
            self.assertTemplateUsed(response, template)

    def check_context(self, response, instance):
        context = response.context
        self.assertEqual(context['object'], instance)
        self.assertIn('image_form', context)
        self.assertIsNotNone(context['image_form'])
        user = context['user']
        if user.is_authenticated:
            self.assertTrue(user.is_authenticated)
            if instance.user() and response.context['user'] == instance.user():
                self.assertIn('user_is_creator', context)
                self.assertTrue(context['user_is_creator'])
                for one in ['already_voted', 'current_user_rating']:
                    self.assertNotIn(one, context)
            else:
                if not instance.is_validated() and user in instance.user_voted.all():
                    self.assertIn('already_voted', context)
                    self.assertTrue(context['already_voted'])
                user_rating = instance.ratings.filter(user_rated=user)
                if user_rating.exists():
                    self.assertIn('current_user_rating', context)
                    self.assertEqual(context['current_user_rating'],  user_rating.get().value)
            questions = instance.questions.all()
            if questions.exists():
                self.assertIn('question_total_dict', context)
                replied_questions = questions.filter(replies__user=user)
                created_questions = questions.filter(user=user)
                question_total_dict = {
                      'Всего вопросов': questions.count(),
                      'Отвечено Вами': replied_questions.count(),
                      'Добавлено Вами': created_questions.count(),
                      'Доступно Вам': questions.count() - replied_questions.count() - created_questions.count(),
                }
                self.assertEqual(context['question_total_dict'],  question_total_dict)
        else:
            self.assertFalse(user.is_authenticated)
            for one in ['user_is_creator', 'already_voted', 'current_user_rating', 'question_total_dict']:
                self.assertNotIn(one, context)

    def check_content(self, response, instance):
        string_list = [
            '<h1>{}</h1>'.format(instance),
            'Данная страница еще не одобрена пользовательским голосованием или командой сайта!',
            'Вы являетесь создателем данной страницы,',
            '<label class="d-inline-block mx-2 my-2 text-dark">{}'.format(str(instance.rating)[0]),
            '<span class="d-inline-block mx-2 my-0 p-0 text-dark">{}</span>',
            'Всего вопросов',
            '<p class="m-0">{}, '.format(instance.validation_status()),
        ]
        pop_list = [0]
        if instance.is_validated():
            pop_list.append(6)
            if instance.user() and response.context['user'] == instance.user():
                pop_list.append(2)
            else:
                pop_list.append(3)
                if self.model == Theme:
                    self.assertContains(response, string_list[4].format(instance.favorite_count()), count = 1)
            if instance.questions.count() > 0:
                pop_list.append(5)
        else:
            pop_list.append(1)
        for i in range(7):
            if i in pop_list:
                self.assertContains(response, string_list[i], count = 1)
            else:
                self.assertNotContains(response, string_list[i])

    def check_response(self, response, instance):
        user = response.context['user']
        self.assertEqual(response.status_code, 200)
        self.check_templates(response, instance)
        self.check_context(response, instance)
        self.check_content(response, instance)

    def create_response(self, instance, user = None):
        url = reverse('core:' + self.url_name, args = [instance.pk])
        # with unauthenticated user
        response_1 = self.client.get(url)
        response_user = response_1.context['user']
        self.assertFalse(response_user.is_authenticated)
        self.check_response(response_1, instance)
        # with authenticated user
        if not user:
            user = AdvUserFactory()
        self.client.force_login(user)
        response_2 = self.client.get(url)
        loged_user = response_2.context['user']
        self.assertTrue(loged_user.is_authenticated)
        self.assertEqual(user, loged_user)
        self.check_response(response_2, instance)

    def test_with_unvalidated_instance(self):
        if self.view:
            instance = self.factory()
            self.create_response(instance)

    def test_with_validated_instance(self):
        if self.view:
            instance = self.factory()
            user = AdvUserFactory(is_staff = True)
            instance.validated_by_staff(user)
            self.assertTrue(instance.is_validated())
            self.create_response(instance)

    def test_then_user_is_creator_of_unvalidated_instance(self):
        if self.view:
            user = AdvUserFactory()
            instance = self.factory(created_by_user_id = user.id)
            self.create_response(instance, user)

    def test_then_user_already_voted_for_unvalidated_instanse(self):
        if self.view:
            user = AdvUserFactory()
            instance = self.factory()
            instance.approved(user)
            self.assertEqual(instance.approve_score, 1)
            self.assertIn(user, instance.user_voted.all())
            self.create_response(instance, user)

    def test_then_user_already_rated_for_validated_instanse(self):
        if self.view:
            user = AdvUserFactory()
            instance = self.factory(is_validated_by_staff = True)
            instance.ratings.create(user_rated = user, value = 5)
            instance.refresh_ratig()
            self.assertEqual(instance.rating, 5)
            self.create_response(instance, user)

    def test_then_there_are_questions(self):
        if self.view:
            instance = self.factory(is_validated_by_staff = True)
            question = QuestionFactory(content_object = instance)
            self.assertEqual(instance.questions.count(), 1)
            self.create_response(instance)

class TestThemeDetailView(UniversalDetailViewTest):
    view = ThemeDetail
    model = Theme
    factory = ThemeFactory
    url_name = 'theme_detail'

class TestPersonDetailView(UniversalDetailViewTest):
    view = PersonDetail
    model = Person
    factory = PersonFactory
    url_name = 'person_detail'

class TestBookDetailView(UniversalDetailViewTest):
    view = BookDetail
    model = Book
    factory = BookFactory
    url_name = 'book_detail'

class TestMovieDetailView(UniversalDetailViewTest):
    view = MovieDetail
    model = Movie
    factory = MovieFactory
    url_name = 'movie_detail'
