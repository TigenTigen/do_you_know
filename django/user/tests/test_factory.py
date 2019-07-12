from django.test import TestCase
from user.factories import AdvUserFactory

class TestAdvUserFactory(TestCase):
    def test_user_creation(self):
        for i in range(10):
            user = AdvUserFactory()
            self.assertIsNotNone(user.id)
            self.assertIsNotNone(user.username)
            self.assertIsNotNone(user.email)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
