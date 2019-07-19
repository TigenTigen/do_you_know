from django.test import TestCase
from django.urls import reverse

from core.models import Cycle
from core.factories import BookFactory

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
