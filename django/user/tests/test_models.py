from django.test import TestCase
from user.factories import AdvUserFactory
from user.models import AdvUser, signer, dt_engine, mail
from django.urls import reverse

class TestAdvUserModel(TestCase):
    def test_str_for_user_created_by_factory(self):
        user = AdvUserFactory(username='some_user')
        self.assertEqual(str(user), 'some_user')

    def test_save_for_user_created_by_social_auth(self):
        user = AdvUser(username='id123456789', first_name='fn', last_name='ln', password='test_password')
        user.save()
        self.assertEqual(user.username, 'fn ln')

    def test_confirm_for_not_active_user(self):
        user = AdvUserFactory(is_active=False)
        self.assertFalse(user.is_active)
        user.confirm()
        self.assertTrue(user.is_active)

    def test_get_email_context(self):
        user = AdvUserFactory()
        link = reverse('user:registration_confirmed', kwargs={'sign': signer.sign(user.username)})
        context = user.get_email_context()
        self.assertIsNotNone(context)
        self.assertIn('confirmation_link', str(context))
        self.assertIn(link, str(context))

    def test_send_confirmation_email(self):
        user = AdvUserFactory()
        link = reverse('user:registration_confirmed', kwargs={'sign': signer.sign(user.username)})
        connection = mail.get_connection(backend='django.core.mail.backends.locmem.EmailBackend')
        outbox = user.send_confirmation_email(connection)
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Подтверждение регистрации')
        self.assertIn(link, outbox[0].body)

    def create_users_for_test(self, number):
        for i in range(number):
            user = AdvUserFactory()
        return AdvUser.objects.all()

    def test_social_count(self):
        users = self.create_users_for_test(10)
        for user in users:
            if user.social_auth.exists():
                self.assertNotEqual(user.social_count(), 0)
            else:
                self.assertEqual(user.social_count(), 0)

    def test_total_points_count(self):
        users = self.create_users_for_test(10)
        for user in users:
            if user.replies.exists():
                self.assertNotEqual(user.total_points_count(), 0)
            else:
                self.assertEqual(user.total_points_count(), 0)

    def test_get_points_rating_queryset_manager_with_users_and_no_replies(self):
        users = self.create_users_for_test(10)
        full_qs = AdvUser.objects.get_queryset()
        test_qs = AdvUser.objects.get_points_rating_queryset()
        self.assertEqual(full_qs.count(), 10)
        self.assertEqual(test_qs.count(), 0)
