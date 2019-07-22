from django.test import TestCase
from django.urls import reverse

from user.factories import AdvUserFactory
from core.models import Question
from core.factories import ThemeFactory, BookFactory, MovieFactory, PersonFactory, QuestionFactory

class Test_create_question(TestCase):
    url = reverse('core:question_create')
    model_list = ['Theme', 'Book', 'Movie', 'Person']
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
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/create/')

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

    def test_theme_question_creation(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        theme = ThemeFactory()
        data = {'model': theme.model(), 'object_id': theme.id, 'question_text': 'test_question_text'}
        response = self.client.post(self.url, data)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, 'test_question_text')
        self.assertEqual(new_question.content_object, theme)
        self.assertEqual(new_question.theme, theme)
        self.assertRedirects(response, reverse('core:add_answers', args = [new_question.pk]))

    def test_book_question_creation(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        theme = ThemeFactory()
        book = BookFactory()
        theme.books.add(book)
        data = {'model': book.model(), 'object_id': book.id, 'question_text': 'test_question_text'}
        response = self.client.post(self.url, data)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, 'test_question_text')
        self.assertEqual(new_question.content_object, book)
        self.assertEqual(new_question.theme, theme)
        self.assertRedirects(response, reverse('core:add_answers', args = [new_question.pk]))

    def test_movie_question_creation(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        theme = ThemeFactory()
        movie = MovieFactory()
        theme.movies.add(movie)
        data = {'model': movie.model(), 'object_id': movie.id, 'question_text': 'test_question_text'}
        response = self.client.post(self.url, data)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, 'test_question_text')
        self.assertEqual(new_question.content_object, movie)
        self.assertEqual(new_question.theme, theme)
        self.assertRedirects(response, reverse('core:add_answers', args = [new_question.pk]))

    def test_person_question_creation(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        person = PersonFactory()
        data = {'model': person.model(), 'object_id': person.id, 'question_text': 'test_question_text'}
        response = self.client.post(self.url, data)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, 'test_question_text')
        self.assertEqual(new_question.content_object, person)
        self.assertRedirects(response, reverse('core:add_answers', args = [new_question.pk]))

class Test_add_answers(TestCase):
    def setUp(self):
        self.user = AdvUserFactory()
        self.theme = ThemeFactory()
        self.question = QuestionFactory(content_object = self.theme, user = self.user)
        self.url = reverse('core:add_answers', args = [self.question.id])
        self.formset_default_data = {
            "answers-TOTAL_FORMS":"4",
            "answers-INITIAL_FORMS":"0",
            "answers-MIN_NUM_FORMS":"0",
            "answers-MAX_NUM_FORMS":"1000",
            "answers-0-text":"",
            "answers-0-question": str(self.question.id),
            "answers-0-id":"",
            "answers-1-text":"",
            "answers-1-question": str(self.question.id),
            "answers-1-id":"",
            "answers-2-text":"",
            "answers-2-question": str(self.question.id),
            "answers-2-id":"",
            "answers-3-text":"",
            "answers-3-question": str(self.question.id),
            "answers-3-id":"",
            "explanation":"",
            "add":"",
        }

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/{}/answers/add/'.format(self.question.id))

    def test_get_with_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/add_answers.html')
        self.assertIsNotNone(response.context['formset'])
        self.assertEqual(len(response.context['formset']), 4)
        self.assertContains(response, self.question.text, count = 1)

    def test_post_with_no_answers(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.formset_default_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/add_answers.html')
        formset = response.context['formset']
        self.assertIsNotNone(formset)
        self.assertEqual(len(formset), 4)
        self.assertFalse(formset.is_valid())
        self.assertIsNotNone(formset.non_form_errors())
        self.assertContains(response, 'Необходимо задать минимум два ответа!', count = 1)

    def test_post_with_one_answer(self):
        self.client.force_login(self.user)
        self.formset_default_data.update({"answers-0-text": "test_answer"})
        response = self.client.post(self.url, self.formset_default_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/add_answers.html')
        formset = response.context['formset']
        self.assertIsNotNone(formset)
        self.assertEqual(len(formset), 4)
        self.assertFalse(formset.is_valid())
        self.assertIsNotNone(formset.non_form_errors())
        self.assertContains(response, 'test_answer', count = 1)
        self.assertContains(response, 'Необходимо задать минимум два ответа!', count = 1)

    def test_post_with_two_answers(self):
        self.client.force_login(self.user)
        self.formset_default_data.update({"answers-0-text": "test_answer_0", "answers-1-text": "test_answer_1",})
        response = self.client.post(self.url, self.formset_default_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/add_answers.html')
        formset = response.context['formset']
        self.assertIsNotNone(formset)
        self.assertEqual(len(formset), 4)
        self.assertFalse(formset.is_valid())
        self.assertIsNotNone(formset.non_form_errors())
        self.assertContains(response, 'test_answer', count = 2)
        self.assertContains(response, 'Необходимо выбрать правильный ответ!', count = 1)

    def test_post_with_two_right_answers(self):
        self.client.force_login(self.user)
        self.formset_default_data.update({"answers-0-text": "test_answer_0", "answers-1-text": "test_answer_1",})
        self.formset_default_data.update({"answers-0-is_right": True, "answers-1-is_right": True,})
        response = self.client.post(self.url, self.formset_default_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/add_answers.html')
        formset = response.context['formset']
        self.assertIsNotNone(formset)
        self.assertEqual(len(formset), 4)
        self.assertFalse(formset.is_valid())
        self.assertIsNotNone(formset.non_form_errors())
        self.assertContains(response, 'test_answer', count = 2)
        self.assertContains(response, 'У вопроса может быть только один правильный ответ!', count = 1)

    def test_post_with_valid_data(self):
        self.client.force_login(self.user)
        self.formset_default_data.update({
            "answers-0-text": "test_answer_0",
            "answers-0-is_right": True,
            "answers-1-text": "test_answer_1",
            "answers-2-text": "test_answer_2",
            "answers-3-text": "test_answer_3",
            "explanation": "Because it is right",
        })
        response = self.client.post(self.url, self.formset_default_data)
        self.assertRedirects(response, reverse('core:question_detail', args = [self.question.pk]))
        updated_question = Question.objects.get(id = self.question.id)
        self.assertEqual(updated_question, self.question)
        self.assertEqual(updated_question.explanation, "Because it is right")
        self.assertEqual(updated_question.answers.count(), 4)
        self.assertEqual(updated_question.right_answer().text, "test_answer_0")

class TestQuestionDetail(TestCase):
    def setUp(self):
        self.user = AdvUserFactory()
        self.theme = ThemeFactory()
        self.question = QuestionFactory(content_object = self.theme)
        self.url = reverse('core:question_detail', args = [self.question.id])

    def test_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/question_datail.html')
        self.assertTemplateUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['object'], self.question)
        for item in ['user_answer', 'user_is_creator', 'current_user_rating']:
            self.assertNotIn(item, response.context)

    def test_with_user_is_creator(self):
        self.client.force_login(self.user)
        self.question.user = self.user
        self.question.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/question_datail.html')
        self.assertTemplateNotUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['object'], self.question)
        self.assertTrue(response.context['user_is_creator'])
        for item in ['user_answer', 'current_user_rating']:
            self.assertNotIn(item, response.context)
        self.assertContains(response, 'Вы являетесь создателем данной страницы,', count = 1)

    def test_with_user_replied(self):
        self.client.force_login(self.user)
        answer = self.question.answers.create(text = 'some_text')
        self.question.replies.create(user = self.user, answer = answer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/question_datail.html')
        self.assertTemplateUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['object'], self.question)
        self.assertIsNotNone(response.context['user_answer'])
        self.assertEqual(response.context['user_answer'], answer)
        for item in ['user_is_creator', 'current_user_rating']:
            self.assertNotIn(item, response.context)
        self.assertInHTML('<label class="text-dark">1: some_text * </label>', response.content.decode('utf-8'), count = 1)

    def test_with_user_rated(self):
        self.client.force_login(self.user)
        self.question.ratings.create(user_rated = self.user, value = 5)
        self.question.refresh_ratig()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/question_datail.html')
        self.assertTemplateUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['object'], self.question)
        self.assertIsNotNone(response.context['current_user_rating'])
        self.assertEqual(response.context['current_user_rating'], 5)
        for item in ['user_answer', 'user_is_creator']:
            self.assertNotIn(item, response.context)
        self.assertInHTML('<i class="material-icons m-0 p-0" style="font-size: 24px; color: green;">star</i>', response.content.decode('utf-8'), count = 5)

class Test_ask_question(TestCase):
    url = reverse('core:ask_question')
    model_list = ['Theme', 'Book', 'Movie', 'Person']
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
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/ask/')

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

    def test_post_with_proper_instance_but_no_questions(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            data = {'model': instance.model(), 'object_id': instance.id}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'questions/ask.html')
            self.assertIsNone(response.context['question'])
            self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 1)

    def test_post_with_valid_data(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for factory in self.factory_list:
            instance = factory()
            question = QuestionFactory(content_object = instance)
            if factory == ThemeFactory:
                question.theme = instance
                question.save()
            self.assertIsNotNone(question.text)
            data = {'model': instance.model(), 'object_id': instance.id}
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'questions/ask.html')
            self.assertEqual(response.context['question'], question)
            self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 0)
            self.assertContains(response, question.text, count = 1)

class Test_ask_similar_question(TestCase):
    def setUp(self):
        self.user = AdvUserFactory()
        self.book = BookFactory()
        self.question = QuestionFactory(content_object = self.book)
        self.url = reverse('core:ask_similar_question', args = [self.question.id])

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/{}/ask/'.format(self.question.pk))

    def test_with_no_instances(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:ask_similar_question', args = [0]))
        self.assertEqual(response.status_code, 404)

    def test_with_no_similar_questions(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertEqual(response.context['question'], self.question)

    def test_with_valid_data(self):
        self.client.force_login(self.user)
        new_question = self.question.content_object.questions.create(text = 'some_text', user = AdvUserFactory())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertEqual(response.context['question'], new_question or self.question)
        self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 0)

class Test_ask_random_question(TestCase):
    url = reverse('core:ask_random_question')

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/ask/random/')

    def test_get_with_authenticated_user_and_no_questions(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertIsNone(response.context['question'])
        self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 1)

    def test_with_question(self):
        user = AdvUserFactory()
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertEqual(response.context['question'], question)
        self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 0)
        self.assertContains(response, question.text, count = 1)

class Test_ask_wellcome_question(TestCase):
    url = reverse('core:ask_wellcome_question')

    def test_get_with_no_questions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertIsNone(response.context['question'])
        self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 1)
        self.assertContains(response, 'Вы не являетесь зарегистрированным пользователем данного сайта.', count = 1)

    def test_with_question(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/ask.html')
        self.assertEqual(response.context['question'], question)
        self.assertContains(response, '<p>Данные отсутсвуют</p>', count = 0)
        self.assertContains(response, question.text, count = 1)
        self.assertContains(response, 'Вы не являетесь зарегистрированным пользователем данного сайта.', count = 1)

class Test_check_answer_for_unautenticated_user(TestCase):
    def test_get(self):
        url = reverse('core:check_answer', args = [1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_with_no_questions(self):
        url = reverse('core:check_answer', args = [1])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_with_question_and_no_data(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        url = reverse('core:check_answer', args = [question.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_with_question_and_no_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': '2'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_with_right_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        answer = question.answers.create(text = 'some_text', is_right = True)
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': answer.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/wellcome_question_reply.html')
        self.assertTemplateUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['question'], question)
        self.assertEqual(response.context['answer'], answer)
        self.assertContains(response, 'Поздравляем, Вы выбрали правильный ответ', count = 1)

    def test_with_wrong_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        answer = question.answers.create(text = 'some_text')
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': answer.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/wellcome_question_reply.html')
        self.assertTemplateUsed(response, 'questions/question_rating_block.html')
        self.assertEqual(response.context['question'], question)
        self.assertEqual(response.context['answer'], answer)
        self.assertContains(response, 'К сожалению, Вы выбрали неправильный ответ.', count = 1)

class Test_check_answer_for_autenticated_user(TestCase):
    def setUp(self):
        self.user = AdvUserFactory()
        self.client.force_login(self.user)

    def test_get(self):
        url = reverse('core:check_answer', args = [1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_with_no_questions(self):
        url = reverse('core:check_answer', args = [1])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_with_question_and_no_data(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        url = reverse('core:check_answer', args = [question.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_with_question_and_no_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': '2'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_with_right_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        answer = question.answers.create(text = 'some_text', is_right = True)
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': answer.pk}
        response = self.client.post(url, data)
        reply = self.user.replies.get()
        self.assertTrue(reply.outcome)
        self.assertEqual(reply.question, question)
        self.assertEqual(reply.answer, answer)
        self.assertRedirects(response, reply.get_absolute_url())

    def test_with_wrong_answer(self):
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        answer = question.answers.create(text = 'some_text')
        url = reverse('core:check_answer', args = [question.pk])
        data = {'checked_answer': answer.pk}
        response = self.client.post(url, data)
        reply = self.user.replies.get()
        self.assertFalse(reply.outcome)
        self.assertEqual(reply.question, question)
        self.assertEqual(reply.answer, answer)
        self.assertRedirects(response, reply.get_absolute_url())

class Test_get_answer(TestCase):
    def test_get_with_unauthenticated_user(self):
        url = reverse('core:get_answer', args=[0])
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/reply/0/get_answer')

    def test_with_no_replies(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        url = reverse('core:get_answer', args = [1])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_with_reply(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        book = BookFactory()
        question = QuestionFactory(content_object = book)
        answer = question.answers.create(text = 'some_text')
        reply = user.replies.create(user = user, question = question, answer = answer)
        url = reverse('core:get_answer', args = [reply.pk])
        response = self.client.post(url)
        self.assertRedirects(response, question.get_absolute_url())

class TestUserCreatedQuestionsListView(TestCase):
    url = reverse('core:created_by_user_questions')

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/core/questions/created_by_user/')

    def test_with_no_questions(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/created_by_user.html')
        self.assertEqual(response.context['object_list'].count(), 0)
        self.assertNotContains(response, '<td>')

    def test_with_questions(self):
        user = AdvUserFactory()
        self.client.force_login(user)
        for i in range(10):
            book = BookFactory()
            if i % 2 == 0:
                QuestionFactory(content_object = book, user = user)
            else:
                QuestionFactory(content_object = book)
        self.assertEqual(user.questions.count(), 5)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/created_by_user.html')
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 5)
        for question in object_list:
            self.assertEqual(question.user, user)
        self.assertContains(response, '<tr>', count = 6)
