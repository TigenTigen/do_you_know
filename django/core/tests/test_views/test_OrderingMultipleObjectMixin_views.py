from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from random import randint, choice
from termcolor import colored

from core.views import ThemeList, PersonList, BookList, MovieList
from core.models import Theme, Person, Book, Movie
from core.factories import ThemeFactory, PersonFactory, BookFactory, MovieFactory

class UniversalListViewTest(TestCase):
    view = None
    model = None
    factory = None
    url_name = None
    template_name = 'core/common_list.html'

    @classmethod
    def setUpTestData(cls):
        if cls.view:
            print(colored('Начинаю тестировать контроллер-класс: {}'.format(cls.view), 'yellow'))
            order_dict = {
                "alphabet_incr": "По алфавиту (А-Я)",
                "alphabet_decr": "По алфавиту (Я-А)",
                "rate_incr": "По возрастанию рейтинга",
                "rate_decr": "По убыванию рейтинга",
                "validated_incr": "По возрастанию даты добавления",
                "validated_decr": "По убыванию даты добавления",
            }
            if cls.model != Theme:
                order_dict.update({
                    "year_incr": "По возрастанию даты создания (рождения)",
                    "yaer_decr": "По убыванию даты создания (рождения)",
                })
            cls.order_dict = order_dict
            cls.pagination_list = [10, 20, 30]
            cls.card_list = ['view_list', 'view_module']
            cls.url = reverse('core:' + cls.url_name)

    @classmethod
    def tearDownClass(cls):
        if cls.view:
            print(colored('Тестирование {} окончено'.format(cls.view), 'green'))
        super().tearDownClass()

    def create_random_instanses(self, N):
        self.assertTrue(False)

    def test_class(self):
        if self.view:
            self.assertEqual(self.view.model, self.model)

    def get_context_dict(self, get_kwargs = {}):
        paginate_by = get_kwargs.get('paginate_by', 10)
        order = get_kwargs.get('order', 'alphabet_incr')
        if 'card_type' in get_kwargs:
            card_type = get_kwargs['card_type']
        elif self.model == Theme:
            card_type = 'view_module'
        else:
            card_type = 'view_list'
        card_path = 'core/cards/{}.html'.format(card_type)
        page_suffix = '&paginate_by={}&order={}&card_type={}'.format(paginate_by, order, card_type)
        context_dict = {
            'paginate_by': paginate_by,
            'pagination_list': self.pagination_list,
            'order': order,
            'order_dict': self.order_dict,
            'card_type': card_type,
            'card_list': self.card_list,
            'card_path': card_path,
            'page_suffix': page_suffix,
        }
        return context_dict

    def check_context_with_get_parameters(self, response, context_dict):
        context = response.context
        self.assertIn(context_dict['paginate_by'], self.pagination_list)
        self.assertLessEqual(context['object_list'].count(), context_dict['paginate_by'])
        self.assertIn(context_dict['order'], self.order_dict.keys())
        self.assertIn(context_dict['card_type'], self.card_list)
        self.assertTemplateUsed(response, context_dict['card_path'])
        for key, value in context_dict.items():
            self.assertIn(key, context)
            self.assertEqual(context[key], value)

    def check_content(self, response, context_dict, object_list_count):
        if object_list_count == 0:
            self.assertContains(response, '<p>Данные отсутствуют</p>', count = 1)
        self.assertContains(response, '<label class="m-0">Всего: {}</label>'.format(object_list_count), count = 1)
        self.assertContains(response, '<strong>{}</strong>'.format(context_dict['paginate_by']), count = 1)
        self.assertContains(response, '<strong>{}</strong>'.format(self.order_dict[context_dict['order']]), count = 1)
        self.assertContains(response, 'color: green">\n                {}'.format(context_dict['card_type']), count = 1)

    def check_pagination(self, response, total_instances_count = 0, page_number = 1):
        paginate_by = response.context['paginate_by']
        object_list_count = response.context['object_list'].count()
        if total_instances_count > paginate_by:
            self.assertIn('page_obj',response.context)
            page_obj = response.context['page_obj']
            self.assertEqual(page_obj.number, page_number)
            if page_number != 1:
                self.assertContains(response, '<u>{}</u></a>'.format(page_number), count = 1)
                self.assertContains(response, '{}</a>'.format(page_number - 1))
            max_page = total_instances_count // paginate_by + 1
            if page_number < max_page:
                self.assertContains(response, '{}</a>'.format(page_number + 1))
                page_object_list_count = paginate_by
            else:
                page_object_list_count = total_instances_count - paginate_by * (page_number - 1)
            self.assertEqual(page_object_list_count, object_list_count)
        else:
            self.assertGreater(paginate_by, total_instances_count)
            self.assertEqual(total_instances_count, object_list_count)
            self.assertNotContains(response, '<div class="mt-auto w-100">')

    def check_ordering(self, order, object_list, created_count):
        qs = self.model.validation.passed()
        ordering_dict = {
            "alphabet_incr": qs.order_by('title'),
            "alphabet_decr": qs.order_by('-title'),
            "year_incr": qs.order_by('year'),
            "yaer_decr": qs.order_by('-year'),
            "rate_incr": qs.order_by('rating'),
            "rate_decr": qs.order_by('-rating'),
            "validated_incr": qs.order_by('validated'),
            "validated_decr": qs.order_by('-validated'),
        }
        ordered_qs = ordering_dict[order]
        self.assertEqual(ordered_qs.count(), created_count)
        self.assertCountEqual(object_list[:10:], ordered_qs[:10:])

    def check_response(self, response, get_kwargs = {}, created_count = 0):
        self.assertEqual(self.model.objects.count(), created_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        object_list_count = response.context['object_list'].count()
        context_dict = self.get_context_dict(get_kwargs)
        self.check_context_with_get_parameters(response, context_dict)
        self.check_content(response, context_dict, object_list_count)
        page = get_kwargs.get('page', 1)
        self.check_pagination(response, created_count, page)
        if page == 1:
            self.check_ordering(get_kwargs.get('order', 'alphabet_incr'), response.context['object_list'], created_count)

    def test_with_different_instanes_number_lesser_then_paginate_by(self):
        if self.view:
            print('...')
            Sum = 0
            for N in [0, 1, 2, 6]:
                for i in range(N):
                    self.factory(is_validated_by_staff = True)
                Sum = Sum + N
                response = self.client.get(self.url)
                self.check_response(response, created_count = Sum)

    def test_with_different_paginate_by(self):
        if self.view:
            print('...')
            Sum = 0
            for paginate_by in self.pagination_list:
                for i in range(paginate_by + 1):
                    self.factory(is_validated_by_staff = True)
                Sum = Sum + paginate_by + 1
                get_kwargs = {'paginate_by': paginate_by}
                response = self.client.get(self.url, get_kwargs)
                self.check_response(response, get_kwargs, Sum)
            for wrong_paginate_by in [-1, 0, 6, 1000]:
                response = self.client.get(self.url, {'paginate_by': wrong_paginate_by})
                self.assertEqual(response.status_code, 404)

    def test_with_different_pages(self):
        if self.view:
            print('...')
            for i in range(33):
                self.factory(is_validated_by_staff = True)
            for page in range(1, 5):
                get_kwargs = {'page': page}
                response = self.client.get(self.url, get_kwargs)
                self.check_response(response, get_kwargs, 33)
            for wrong_page_number in [-1, 0, 6, 1000, 'a']:
                response = self.client.get(self.url, {'page': wrong_page_number})
                self.assertEqual(response.status_code, 404)

    def test_with_different_card_types(self):
        if self.view:
            print('...')
            for i in range(3):
                self.factory(is_validated_by_staff = True)
            for card_type in self.card_list:
                get_kwargs = {'card_type': card_type}
                response = self.client.get(self.url, get_kwargs)
                self.check_response(response, get_kwargs, 3)
            for wrong_card_type in [-1, 0, 6, 1000, 'a']:
                response = self.client.get(self.url, {'card_type': wrong_card_type})
                self.assertEqual(response.status_code, 404)

    def test_with_different_ordering(self):
        if self.view:
            print('...')
            Sum = 0
            for j in range(3):
                self.create_random_instanses(3)
                Sum = Sum + 3
                for order in self.order_dict.keys():
                    get_kwargs = {'order': order}
                    response = self.client.get(self.url, get_kwargs)
                    self.check_response(response, get_kwargs, Sum)
            for wrong_order in [-1, 0, 6, 1000, 'a']:
                response = self.client.get(self.url, {'order': wrong_order})
                self.assertEqual(response.status_code, 404)

    def test_with_random_get_kwargs(self):
        if self.view:
            N = randint(5, 25)
            self.create_random_instanses(N)
            random_paginate_by = choice(self.pagination_list)
            get_kwargs = {
                'paginate_by': random_paginate_by,
                'page': randint(1, N // random_paginate_by + 1),
                'order': choice([i for i in self.order_dict.keys()]),
                'card_type': choice(self.card_list),
            }
            response = self.client.get(self.url, get_kwargs)
            self.check_response(response, get_kwargs, N)
            print(colored('Контрольный тест на {} объектах с произвольными параметрами: {}, прошел успешно'.format(N, get_kwargs), 'green'))

class TestThemeList(UniversalListViewTest):
    view = ThemeList
    model = Theme
    factory = ThemeFactory
    url_name = 'theme_list'

    def create_random_instanses(self, N):
        for i in range(N):
            self.factory(
                is_validated_by_staff = True,
                rating = randint(0, 5),
                validated = timezone.now(),
            )

class TestPersonList(UniversalListViewTest):
    view = PersonList
    model = Person
    factory = PersonFactory
    url_name = 'person_list'

    def create_random_instanses(self, N):
        for i in range(N):
            self.factory(
                is_validated_by_staff = True,
                born = timezone.now(),
                rating = randint(0, 5),
                validated = timezone.now(),
            )

class TestBookList(UniversalListViewTest):
    view = BookList
    model = Book
    factory = BookFactory
    url_name = 'book_list'

    def create_random_instanses(self, N):
        for i in range(N):
            self.factory(
                is_validated_by_staff = True,
                year = randint(2000, 2020),
                rating = randint(0, 5),
                validated = timezone.now(),
            )

class TestMovieList(UniversalListViewTest):
    view = MovieList
    model = Movie
    factory = MovieFactory
    url_name = 'movie_list'

    def create_random_instanses(self, N):
        for i in range(N):
            self.factory(
                is_validated_by_staff = True,
                year = randint(2000, 2020),
                rating = randint(0, 5),
                validated = timezone.now(),
            )
