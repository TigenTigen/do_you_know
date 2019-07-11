from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from contacts.views import *
from contacts.forms import *
from contacts.models import *

AUTH_USER_MODEL = get_user_model()

class UniversalURLtest(SimpleTestCase):
    simple_url_view_dict = {}
    app_name = ''
    namespace = ''

    def test_resolve_url(self):
        for url in self.simple_url_view_dict.keys():
            resolved_url = resolve(reverse(self.namespace + ':' + url))
            self.assertEqual(resolved_url.app_name, self.app_name)
            self.assertEqual(resolved_url.namespace, self.namespace)
            try:
                self.assertEqual(resolved_url.func.view_class, self.simple_url_view_dict[url])
            except:
                self.assertEqual(resolved_url.func, self.simple_url_view_dict[url])

class TestURLs(UniversalURLtest):
    simple_url_view_dict = {
        'message_list': MessageListView,
        'message_create': MessageCreateView,
        'faq': FAQListView,
    }
    app_name = 'contacts'
    namespace = 'contacts'

    def test_message_reply_resolve(self):
        url = reverse('contacts:message_reply', args=[1])
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func.view_class, ReplyCreateView)

    def test_add_to_faq_resolve(self):
        url = reverse('contacts:add_to_faq', args=[1])
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, add_to_faq)

class TestViews_for_unauthenticated_user(TestCase):
    client = Client()

    def setUp(self):
        self.category1 = Category.objects.create(title='category1')

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
        self.category1 = Category.objects.create(title='category1')
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
        self.category1 = Category.objects.create(title='category1')
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
