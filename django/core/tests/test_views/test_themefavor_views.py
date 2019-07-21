from django.test import TestCase
from django.urls import reverse

from core.factories import ThemeFactory
from user.factories import AdvUserFactory

class TestFavouriteThemeList(TestCase):
    url = reverse('core:favorite_by_user')

    def test_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/themes/favorite/user/')

    def test_with_no_instances(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/common_list.html')
        self.assertEqual(response.context['object_list'].count(), 0)
        self.assertContains(response, 'Данные отсутствуют', count = 1)

    def test_with_instances(self):
        user = AdvUserFactory()
        for i in range(10):
            theme = ThemeFactory(is_validated_by_staff = True)
            if i % 2 == 0:
                user.favorite_themes.add(theme)
        self.assertEqual(user.favorite_themes.count(), 5)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/common_list.html')
        self.assertNotContains(response, 'Данные отсутствуют')
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 5)
        for object in object_list:
            self.assertIn(user, object.favorited_by.all())

class Test_favorite(TestCase):
    def test_get_with_unauthenticated_user(self):
        url = reverse('core:favorite', args = [1])
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=/core/themes/favorite/1/')

    def test_with_not_existing_theme(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        url = reverse('core:favorite', args = [1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_with_existing_theme(self):
        theme = ThemeFactory()
        user = AdvUserFactory()
        self.client.force_login(user)
        url = reverse('core:favorite', args = [theme.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(user, theme.favorited_by.all())

    def test_with_theme_already_favored(self):
        theme = ThemeFactory()
        user = AdvUserFactory()
        user.favorite_themes.add(theme)
        self.assertIn(user, theme.favorited_by.all())
        self.client.force_login(user)
        url = reverse('core:favorite', args = [theme.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(user, theme.favorited_by.all())
