from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from core.models import Question, Answer, UserReplyRecord
from core.factories import ThemeFactory, QuestionFactory, AnswerFactory, ReplyFactory, RatingFactory
from user.factories import AdvUserFactory
from random import shuffle

class TestQuestionModel(TestCase):
    def setUp(self):
        self.theme = ThemeFactory()

    def test_meta_ordering(self):
        for i in range(10):
            QuestionFactory(content_object = self.theme)
        questions = Question.objects.all()
        self.assertEqual(questions.count(), 10)
        check_data = timezone.now()
        for question in questions:
            self.assertLess(question.created, check_data)
            check_data = question.created

    def test_str(self):
        question = QuestionFactory(content_object = self.theme)
        self.assertEqual(str(question), question.text)

    def test_get_absolute_url(self):
        question = QuestionFactory(content_object = self.theme)
        self.assertEqual(question.get_absolute_url(), '/core/questions/{}/'.format(question.pk))
        self.assertEqual(question.get_absolute_url(), reverse('core:question_detail', args=[question.pk]))

    def test_right_answer(self):
        # no answers
        question = QuestionFactory(content_object = self.theme)
        self.assertIsNone(question.right_answer())
        with self.assertRaises(ObjectDoesNotExist):
            Question.objects.get(id=question.id)
        # one not right answer
        question = QuestionFactory(content_object = self.theme)
        answer = AnswerFactory(question = question)
        self.assertIsNone(question.right_answer())
        with self.assertRaises(ObjectDoesNotExist):
            Question.objects.get(id=question.id)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(id=answer.id)
        # two right questions
        question = QuestionFactory(content_object = self.theme)
        answer1 = AnswerFactory(question = question, is_right = True)
        answer2 = AnswerFactory(question = question, is_right = True)
        self.assertIsNone(question.right_answer())
        with self.assertRaises(ObjectDoesNotExist):
            Question.objects.get(id=question.id)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(id=answer1.id)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(id=answer2.id)
        # one right answer
        question = QuestionFactory(content_object = self.theme)
        answer1 = AnswerFactory(question = question, is_right = True)
        answer2 = AnswerFactory(question = question)
        answer = question.right_answer()
        self.assertIsNotNone(answer)
        self.assertTrue(answer.is_right)
        self.assertEqual(answer.question, question)

    def test_get_random_question_with_no_replies(self):
        user = AdvUserFactory()
        # no questions
        self.assertIsNone(Question.objects.get_random_question(user))
        # with prepopulated questions
        for i in range(10):
            if i % 3 == 0:
                QuestionFactory(content_object = self.theme, user = user)
            else:
                QuestionFactory(content_object = self.theme)
        self.assertEqual(Question.objects.all().count(), 10)
        for i in range(10):
            question = Question.objects.get_random_question(user)
            self.assertIsNotNone(question.id)
            self.assertNotEqual(question.user, user)

    def test_get_random_question(self):
        user = AdvUserFactory()
        for i in range(30):
            if i % 3 == 0:
                QuestionFactory(content_object = self.theme, user = user)
            elif i % 3 == 1:
                question = QuestionFactory(content_object = self.theme)
                answer = AnswerFactory(question = question)
                reply = ReplyFactory(user = user, question = question, answer = answer)
            else:
                QuestionFactory(content_object = self.theme)
        self.assertEqual(Question.objects.all().count(), 30)
        for i in range(10):
            question = Question.objects.get_random_question(user)
            self.assertIsNotNone(question.id)
            self.assertNotEqual(question.user, user)
            self.assertNotEqual(user, question.user)

    def test_user_created(self):
        user = AdvUserFactory()
        for i in range(10):
            if i % 2 == 0:
                QuestionFactory(content_object = self.theme, user = user)
            else:
                QuestionFactory(content_object = self.theme)
        self.assertEqual(Question.objects.all().count(), 10)
        user_created = Question.objects.user_created(user)
        self.assertEqual(user_created.count(), 5)
        for question in user_created:
            self.assertEqual(question.user, user)

    def test_get_wellcome_question(self):
        for i in range(5):
            QuestionFactory(content_object = self.theme, rating = i)
        self.assertEqual(Question.objects.get_wellcome_question(), Question.objects.first())

    def test_refresh_ratig(self):
        question = QuestionFactory(content_object = self.theme)
        # no rating reports
        self.assertEqual(question.rating, 0)
        # one rating report
        rating = RatingFactory(content_object = question)
        question.refresh_ratig()
        self.assertEqual(question.rating, rating.value)
        # many rating reports
        sum = rating.value
        for i in range(20):
            if i % 2 == 0:
                rating = RatingFactory(content_object = question)
                sum = sum + rating.value
            else:
                over_question = QuestionFactory(content_object = ThemeFactory())
                RatingFactory(content_object = over_question)
        question.refresh_ratig()
        self.assertEqual(question.ratings.count(), 11)
        self.assertEqual(round(question.rating, 2), round(sum/11, 2))

class TestAnswerModel(TestCase):
    def setUp(self):
        self.theme = ThemeFactory()
        self.question = QuestionFactory(content_object = self.theme)

    def test_meta_ordering_for_answers_of_one_question(self):
        letter_list = ['a', 'b', 'c', 'd']
        letter_list_copy = letter_list.copy()
        shuffle(letter_list_copy)
        for letter in letter_list_copy:
            AnswerFactory(text = letter, question = self.question)
        answers = Answer.objects.all()
        self.assertEqual(answers.count(), 4)
        self.assertEqual(self.question.answers.all().count(), 4)
        i = 0
        for answer in answers:
            self.assertEqual(answer.text, letter_list[i])
            i = i + 1

    def test_meta_ordering_for_answers_with_questions(self):
        for i in range(10):
            question = QuestionFactory(content_object = self.theme)
            answer = AnswerFactory(question = question)
        answers = Answer.objects.all()
        self.assertEqual(answers.count(), 10)
        check_id = answers.last().question.id + 1
        for answer in answers.reverse():
            self.assertLess(answer.question.id, check_id)
            check_id = answer.question.id

    def test_str(self):
        answer = AnswerFactory(question = self.question)
        self.assertEqual(str(answer), answer.text)

    def test_color(self):
        self.assertEqual(AnswerFactory(question = self.question).color(), 'text-dark')
        self.assertEqual(AnswerFactory(question = self.question, is_right=True).color(), 'text-success')

    def test_frequence(self):
        answer1 = AnswerFactory(question = self.question, is_right = True)
        self.assertEqual(answer1.frequence(), 0)
        answer2 = AnswerFactory(question = self.question)
        self.assertEqual(answer2.frequence(), 0)
        answer3 = AnswerFactory(question = self.question)
        self.assertEqual(answer3.frequence(), 0)
        answer4 = AnswerFactory(question = self.question)
        self.assertEqual(answer4.frequence(), 0)
        self.assertEqual(Answer.objects.all().count(), 4)
        for i in range(40):
            if i % 4 == 0:
                ReplyFactory(question = self.question, answer = answer1)
            else:
                ReplyFactory(question = self.question, answer = answer2)
        self.assertEqual(UserReplyRecord.objects.all().count(), 40)
        self.assertEqual(answer1.frequence(), 25)
        self.assertEqual(answer2.frequence(), 75)
        self.assertEqual(answer3.frequence(), 0)
        self.assertEqual(answer4.frequence(), 0)

    def test_points(self):
        answer1 = AnswerFactory(question = self.question, is_right = True)
        answer2 = AnswerFactory(question = self.question)
        answer3 = AnswerFactory(question = self.question)
        answer4 = AnswerFactory(question = self.question)
        self.assertEqual(Answer.objects.all().count(), 4)
        for i in range(20):
            if i % 2 == 0:
                ReplyFactory(question = self.question, answer = answer1)
            else:
                ReplyFactory(question = self.question, answer = answer2)
        self.assertEqual(UserReplyRecord.objects.all().count(), 20)
        self.assertEqual(answer1.points(), 6)
        self.assertEqual(answer2.points(), 0)
        self.assertEqual(answer3.points(), 0)
        self.assertEqual(answer4.points(), 0)
