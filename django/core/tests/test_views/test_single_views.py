from django.test import TestCase
from django.urls import reverse

from core.models import Cycle, Question
from core.factories import ThemeFactory, BookFactory, MovieFactory, PersonFactory, QuestionFactory
from user.factories import AdvUserFactory

class TestCycleDetailView(TestCase):
    def test_with_no_cycle(self):
        url = reverse('core:cycle_detail', args = [1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_with_cycle_and_no_numbers(self):
        cycle = Cycle.objects.create(title = 'test_title')
        url = reverse('core:cycle_detail', args = [cycle.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cycle_detail.html')
        self.assertEqual(response.context['object'], cycle)
        self.assertContains(response, '<h1>test_title</h1>', count = 1)
        self.assertNotContains(response, '<li>')

    def test_with_cycle_and_number(self):
        book = BookFactory()
        cycle = Cycle.objects.create(title = 'test_title')
        number = cycle.number_set.create(number = 1, book = book)
        url = reverse('core:cycle_detail', args = [cycle.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cycle_detail.html')
        self.assertEqual(response.context['object'], cycle)
        self.assertContains(response, str(number.object()), count = 1)
        self.assertContains(response, str(number.object().get_absolute_url()), count = 1)

class Test_rate(TestCase):
    url = reverse('core:rate')
    model_list = ['Theme', 'Book', 'Movie', 'Person', 'Question']
    factory_list = [ThemeFactory, BookFactory, MovieFactory, PersonFactory]

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
        self.assertRedirects(response, '/accounts/login/?next=/core/rate/')

    def test_post_with_authenticated_user_and_no_data(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_with_no_instances(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for model_name in self.model_list:
            data = {'model': model_name, 'object_id': 1, 'value': 5}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 404)

    def test_with_instances_not_rated(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            data = {'model': instance.model(), 'object_id': instance.id, 'value': 5}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            updated_instance = factory._meta.model.objects.get(id = instance.id)
            self.assertEqual(instance, updated_instance)
            self.assertEqual(updated_instance.rating, 5)
            self.assertEqual(updated_instance.ratings.count(), 1)
            self.assertEqual(updated_instance.ratings.get().user_rated, user)

    def test_with_instances_rated_before_by_the_user(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            instance.ratings.create(user_rated = user, value = 3)
            instance.refresh_ratig()
            self.assertEqual(instance.rating, 3)
            self.assertEqual(instance.ratings.count(), 1)
            self.assertEqual(instance.ratings.get().user_rated, user)
            data = {'model': instance.model(), 'object_id': instance.id, 'value': 5}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            updated_instance = factory._meta.model.objects.get(id = instance.id)
            self.assertEqual(instance, updated_instance)
            self.assertEqual(updated_instance.rating, 5)
            self.assertEqual(updated_instance.ratings.count(), 1)
            self.assertEqual(updated_instance.ratings.get().user_rated, user)

    def test_with_questions_not_rated(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            question = QuestionFactory(content_object = instance)
            data = {'model': 'Question', 'object_id': question.id, 'value': 5}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            updated_question = Question.objects.get(id = question.id)
            self.assertEqual(question, updated_question)
            self.assertEqual(updated_question.rating, 5)
            self.assertEqual(updated_question.ratings.count(), 1)
            self.assertEqual(updated_question.ratings.get().user_rated, user)

    def test_with_questions_rated_before_by_the_user(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            question = QuestionFactory(content_object = instance)
            question.ratings.create(user_rated = user, value = 3)
            question.refresh_ratig()
            self.assertEqual(question.rating, 3)
            self.assertEqual(question.ratings.count(), 1)
            self.assertEqual(question.ratings.get().user_rated, user)
            data = {'model': 'Question', 'object_id': question.id, 'value': 5}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            updated_question = Question.objects.get(id = question.id)
            self.assertEqual(question, updated_question)
            self.assertEqual(updated_question.rating, 5)
            self.assertEqual(updated_question.ratings.count(), 1)
            self.assertEqual(updated_question.ratings.get().user_rated, user)
