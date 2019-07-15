from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from contacts.views import *
from contacts.forms import *
from contacts.models import *
from config.universal_tests import UniversalURLtest
from contacts.urls import urlpatterns
from config.universal_tests import UniversalFormTest

AUTH_USER_MODEL = get_user_model()

class TestURLs(UniversalURLtest):
    app_name = 'contacts'
    namespace = 'contacts'
    urlpatterns = urlpatterns

class TestViews_for_unauthenticated_user(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(title='category1')

    def test_MessageListView_with_no_messages(self):
        response = self.client.get(reverse('contacts:message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/message_list.html')
        self.assertEqual(response.context['object_list'].count(), 0)
        self.assertContains(response, 'Данные отсутствуют', count=1)
        self.assertNotContains(response, 'strong')

    def test_MessageListView(self):
        for i in range(10):
            new_message = AnonymousMessage.objects.create(
                name = 'AnonymousUser',
                email = 'anon@test.com',
                category = self.category1,
                title = 'title' + str(i),
                text = 'some_text',
                is_private = (i % 2 == 0), # that meens only half of messages are private, therefor are visible on list page
            )
        response = self.client.get(reverse('contacts:message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/message_list.html')
        self.assertEqual(Message.objects.count(), 10)
        self.assertEqual(response.context['object_list'].count(), 5)
        self.assertContains(response, 'some_text', count=5)
        self.assertNotContains(response, 'Добавить в  FAQ')
        self.assertNotContains(response, 'Ответить на сообщение')

    def test_MessageCreateView_GET(self):
        response = self.client.get(reverse('contacts:message_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/message_create_form.html')
        self.assertIsInstance(response.context['form'], AnonymousMessageForm)

    def test_MessageCreateView_POST_no_data(self):
        response = self.client.post(reverse('contacts:message_create'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(Message.objects.count(), 0)

    def check_form_if_no_redirect(response):
        form = response.context['form']
        self.assertFalse(form.is_valid())
        print('Form is invalid!')
        if form.non_field_errors:
            print(form.non_field_errors)
        for field in form:
            if field.errors:
                print(field.name, field.errors)

    def test_MessageCreateView_POST(self):
        response = self.client.post(reverse('contacts:message_create'), {
            'name': 'AnonymousUser',
            'email': 'anon@test.com',
            'category': self.category1.id,
            'title': 'some_title',
            'text': 'some_text',
        })
        if response.status_code == 200:
            check_form_if_no_redirect(response)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(AnonymousMessage.objects.count(), 1)
            self.assertEqual(Message.objects.count(), 1)
            self.assertEqual(AnonymousMessage.objects.first().name, 'AnonymousUser')
            self.assertEqual(AnonymousMessage.objects.first().is_private, False)
            self.assertEqual(AnonymousMessage.objects.first().category, self.category1)

class TestViews_for_authenticated_user(TestViews_for_unauthenticated_user):
    def setUp(self):
        self.user, created = AUTH_USER_MODEL.objects.get_or_create(username='testuser1')
        self.client.force_login(self.user)

    def test_force_login(self):
        response = self.client.get(reverse('contacts:message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_MessageCreateView_GET(self):
        response = self.client.get(reverse('contacts:message_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/message_create_form.html')
        self.assertIsInstance(response.context['form'], UserMessageForm)

    def test_MessageCreateView_POST(self):
        response = self.client.post(reverse('contacts:message_create'), {
            'user': self.user.id,
            'category': self.category1.id,
            'title': 'some_title',
            'text': 'some_text',
        })
        if response.status_code == 200:
            check_form_if_no_redirect(response)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(UserMessage.objects.count(), 1)
            self.assertEqual(Message.objects.count(), 1)
            self.assertEqual(UserMessage.objects.first().text, 'some_text')
            self.assertEqual(UserMessage.objects.first().is_private, False)
            self.assertEqual(UserMessage.objects.first().category, self.category1)
            self.assertEqual(self.user.messages.count(), 1)

class TestViews_for_staff_user(TestViews_for_authenticated_user):
    def setUp(self):
        self.user, created = AUTH_USER_MODEL.objects.get_or_create(username='staff_user', is_staff=True)
        self.client.force_login(self.user)

    def test_force_login(self):
        response = self.client.get(reverse('contacts:message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_staff)

    def test_MessageListView(self):
        for i in range(10):
            new_message = AnonymousMessage.objects.create(
                name = 'AnonymousUser',
                email = 'anon@test.com',
                category = self.category1,
                title = 'title' + str(i),
                text = 'some_text',
                is_private = (i % 2 == 0), # that meens only half of messages are private, therefor are visible on list page
            )
        response = self.client.get(reverse('contacts:message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/message_list.html')
        self.assertEqual(Message.objects.count(), 10)
        self.assertEqual(response.context['object_list'].count(), 10)
        self.assertContains(response, 'some_text', count=10)
        self.assertContains(response, 'Добавить в  FAQ')
        self.assertContains(response, 'Ответить на сообщение')

    def get_message_id(self):
        message = AnonymousMessage.objects.create(
            name = 'AnonymousUser',
            email = 'anon@test.com',
            category = self.category1,
            title = 'title',
            text = 'some_text',
        )
        return message.id

    def test_ReplyCreateView_GET(self):
        url = reverse('contacts:message_reply', args=[self.get_message_id()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/reply_create_form.html')
        self.assertIsInstance(response.context['form'], ReplyForm)
        self.assertIn('user', response.context['form'].fields)
        self.assertIn('message', response.context['form'].fields)

    def test_ReplyCreateView_POST_no_data(self):
        url = reverse('contacts:message_reply', args=[self.get_message_id()])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(Reply.objects.count(), 0)

    def test_ReplyCreateView_POST(self):
        url = reverse('contacts:message_reply', args=[self.get_message_id()])
        response = self.client.post(url, {
            'text': 'some_text',
            'user': self.user.id,
            'message': self.get_message_id(),
        })
        if response.status_code == 200:
            self.check_form_if_no_redirect(response)
        else:
            self.assertRedirects(response, reverse('contacts:message_list'))
            self.assertEqual(Reply.objects.count(), 1)
            self.assertEqual(Reply.objects.first().text, 'some_text')
            self.assertEqual(self.user.reply_set.count(), 1)

    def test_add_to_faq_for_message_with_no_replies(self):
        message = AnonymousMessage.objects.create(
            name = 'AnonymousUser',
            email = 'anon@test.com',
            category = self.category1,
            title = 'title',
            text = 'some_text',
        )
        url = reverse('contacts:add_to_faq', args=[message.id])
        response = self.client.get(url)
        self.assertFalse(message.show_as_faq)

    def test_add_to_faq(self):
        # create message with reply
        message = AnonymousMessage.objects.create(
            name = 'AnonymousUser',
            email = 'anon@test.com',
            category = self.category1,
            title = 'title',
            text = 'some_text',
        )
        reply = Reply.objects.create(
            message = message,
            user = self.user,
            text = 'test_reply_texr'
        )
        self.assertEqual(message.replies.count(), 1)
        # move message to faq
        url = reverse('contacts:add_to_faq', args=[message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # check faq page: message is displayed on faq page
        response = self.client.get(reverse('contacts:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contacts/faq.html')
        self.assertContains(response, 'some_text', count=1)
        self.assertEqual(response.context['object_list'].count(), 1)
        updated_message = response.context['object_list'][0].anon
        self.assertEqual(updated_message.id, message.id)
        self.assertTrue(updated_message.show_as_faq)

class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user, created = AUTH_USER_MODEL.objects.get_or_create(username='test_user')
        cls.category = Category.objects.create(title='test_category')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'test_category')

    def test_message_str(self):
        message = Message.objects.create(title='test_title', text='test_text', category=self.category)
        self.assertEqual(str(message), 'test_title')
        self.assertIsNotNone(message.created)

    def test_usermessage_str(self):
        usermessage = UserMessage.objects.create(title='test_title', text='test_text', category=self.category, user=self.user)
        self.assertEqual(str(usermessage), 'test_user (Пользователь)')

    def test_anonymoususer_str(self):
        anonmessage = AnonymousMessage.objects.create(
            title = 'test_title',
            text = 'test_text',
            category = self.category,
            name = 'test_name',
            email = 'test_email',
        )
        self.assertEqual(str(anonmessage), 'test_name (Гость)')

class TestUserMessageForm(UniversalFormTest):
    form_class = UserMessageForm
    form_model_class = UserMessage

    def get_valid_data_dict(self):
        category, created = Category.objects.get_or_create(title='test_category')
        user, created = AUTH_USER_MODEL.objects.get_or_create(username='test_user')
        data_dict = {
            'category': category.id,
            'title': 'some_text',
            'text': 'some_text',
            'user': user.id,
        }
        return data_dict

    def get_field_validation_check_dict(self):
        field_validation_check_dict = {
            'title': {
                'wrong_choices': [None, '', '  ', ],
                'right_choices': [1, 'some_string', 'some title'],
            },
            'text': {
                'wrong_choices': [None, '', '  ', ],
                'right_choices': [1, 'some_string', 'some string'],
            },
        }
        return field_validation_check_dict

class TestAnonymousMessageForm(UniversalFormTest):
    form_class = AnonymousMessageForm
    form_model_class = AnonymousMessage

    def get_valid_data_dict(self):
        category, created = Category.objects.get_or_create(title='test_category')
        data_dict = {
            'category': category.id,
            'title': 'some_text',
            'text': 'some_text',
            'name': 'some_text',
            'email': 'some@email.com'
        }
        return data_dict

    def get_field_validation_check_dict(self):
        field_validation_check_dict = {
            'title': {
                'wrong_choices': [None, '', '  '],
                'right_choices': [1, 'some_string', 'some title'],
            },
            'text': {
                'wrong_choices': [None, '', '  '],
                'right_choices': [1, 'some_string', 'some string'],
            },
            'email': {
                'wrong_choices': [None, '', '  ', 1, 'some_string', 'some string', 'some@email@com', 'some@email'],
                'right_choices': ['some@email.com'],
            },
        }
        return field_validation_check_dict

class TestReplyForm(UniversalFormTest):
    form_class = ReplyForm
    form_model_class = Reply

    def get_valid_data_dict(self):
        category, created = Category.objects.get_or_create(title='test_category')
        message, created = Message.objects.get_or_create(title='title', text='text', category=category)
        user, created = AUTH_USER_MODEL.objects.get_or_create(username='test_user')
        data_dict = {
            'user': user.id,
            'text': 'some_text',
            'message': message.id,
        }
        return data_dict
