from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user
from core.models import Theme, Person, Book, Movie, Question
from core.factories import *
from user.factories import AdvUserFactory
from random import shuffle
from datetime import datetime

class TestValidatedModel(TestCase):
    model = None
    model_factory = None

    def get_updated_instance(self, instance):
        updated_instance = self.model.objects.get(id=instance.id)
        self.assertEqual(updated_instance.id, instance.id)
        return updated_instance

    def test_is_validated(self):
        if self.model_factory:
            self.assertFalse(self.model_factory().is_validated())
            self.assertTrue(self.model_factory(is_validated_by_staff=True).is_validated())
            self.assertTrue(self.model_factory(is_validated_by_users=True).is_validated())

    def test_color(self):
        if self.model_factory:
            self.assertEqual(self.model_factory().color(), 'text-muted')
            self.assertEqual(self.model_factory(is_validated_by_staff=True).color(), 'text-dark')

    def test_user(self):
        if self.model_factory:
            user = AdvUserFactory()
            instance = self.model_factory(created_by_user_id=user.id)
            self.assertEqual(instance.user(), user)

    def test_staff(self):
        if self.model_factory:
            user = AdvUserFactory()
            instance = self.model_factory(validated_by_staff_id=user.id)
            self.assertEqual(instance.staff(), user)

    def test_target(self):
        if self.model_factory:
            self.assertEqual(self.model_factory().target(), 5)

    def test_validated_by_staff_with_staff_user(self):
        if self.model_factory:
            user = AdvUserFactory(is_staff = True)
            instance = self.model_factory()
            instance.validated_by_staff(user)
            updated_instance = self.get_updated_instance(instance)
            self.assertTrue(updated_instance.is_validated_by_staff)
            self.assertIsNotNone(updated_instance.validated)
            self.assertEqual(updated_instance.validated_by_staff_id, user.id)

    def test_validated_by_staff_with_not_staff_user(self):
        if self.model_factory:
            user = AdvUserFactory()
            instance = self.model_factory()
            instance.validated_by_staff(user)
            updated_instance = self.get_updated_instance(instance)
            self.assertFalse(updated_instance.is_validated_by_staff)
            self.assertIsNone(updated_instance.validated)
            self.assertNotEqual(updated_instance.validated_by_staff_id, user.id)

    def test_approved(self):
        if self.model_factory:
            user = AdvUserFactory()
            for i in range(5):
                instance = self.model_factory(approve_score=i)
                instance.approved(user)
                updated_instance = self.get_updated_instance(instance)
                self.assertEqual(updated_instance.approve_score, i+1)
                self.assertIn(user, updated_instance.user_voted.all())
                if i == 4:
                    self.assertTrue(updated_instance.is_validated_by_users)
                    self.assertIsNotNone(updated_instance.validated)
                else:
                    self.assertFalse(updated_instance.is_validated_by_users)
                    self.assertIsNone(updated_instance.validated)

    def test_disapproved(self):
        if self.model_factory:
            user = AdvUserFactory()
            for i in range(5):
                instance = self.model_factory(approve_score=i)
                instance.disapproved(user)
                updated_instance = self.get_updated_instance(instance)
                self.assertEqual(updated_instance.approve_score, i-1)
                self.assertIn(user, updated_instance.user_voted.all())

    def test_validation_status(self):
        if self.model_factory:
            self.assertEqual(self.model_factory(is_validated_by_staff=True).validation_status(), 'одобрено командой сайта')
            self.assertEqual(self.model_factory(is_validated_by_users=True).validation_status(), 'одобрено по итогам голосования пользователей')
            for i in range(5):
                self.assertEqual(self.model_factory(approve_score=i).validation_status(), 'текущий уровень одобрения: {}'.format(i))

    def test_passed(self):
        if self.model_factory:
            for i in range(30):
                instance = self.model_factory(is_validated_by_staff=(i%3==0), is_validated_by_users=(i%3==1))
            all = self.model.objects.all()
            passed = self.model.validation.passed()
            self.assertEqual(passed.count(), 20)
            for instance in all:
                if instance.is_validated():
                    self.assertIn(instance, passed)
                else:
                    self.assertNotIn(instance, passed)

    def test_current_for_unauthenticated_user(self):
        if self.model_factory:
            user = get_user(self.client)
            self.assertFalse(user.is_authenticated)
            for i in range(30):
                instance = self.model_factory(is_validated_by_staff=(i%3==0), is_validated_by_users=(i%3==1))
            all = self.model.objects.all()
            current = self.model.validation.current(user)
            self.assertEqual(current.count(), 10)
            for instance in all:
                if instance.is_validated():
                    self.assertNotIn(instance, current)
                else:
                    self.assertIn(instance, current)
            for instance in current:
                self.assertNotIn('vote_count', vars(instance))
                self.assertNotIn('already_voted', vars(instance))
                self.assertNotIn('user_is_creator', vars(instance))

    def test_current_for_authenticated_user(self):
        if self.model_factory:
            user = AdvUserFactory()
            self.assertTrue(user.is_authenticated)
            for i in range(30):
                instance = self.model_factory(is_validated_by_staff=(i%3==0), is_validated_by_users=(i%3==1))
            all = self.model.objects.all()
            current = self.model.validation.current(user)
            self.assertEqual(current.count(), 10)
            for instance in all:
                if instance.is_validated():
                    self.assertNotIn(instance, current)
                else:
                    self.assertIn(instance, current)
            for instance in current:
                self.assertIn('vote_count', vars(instance))
                self.assertIn('already_voted', vars(instance))
                self.assertIn('user_is_creator', vars(instance))
                self.assertIsNotNone(instance.vote_count)
                self.assertIsNotNone(instance.already_voted)
                self.assertIsNotNone(instance.user_is_creator)

    def test_user_created(self):
        if self.model_factory:
            user = AdvUserFactory()
            self.assertTrue(user.is_authenticated)
            for i in range(10):
                instance = self.model_factory(created_by_user_id=(user.id if i % 2 == 0 else None))
            all = self.model.objects.all()
            user_created = self.model.validation.user_created(user.id)
            self.assertEqual(user_created.count(), 5)
            for instance in all:
                if instance.created_by_user_id == user.id:
                    self.assertIn(instance, user_created)
                else:
                    self.assertNotIn(instance, user_created)

    def test_get_question_to_ask(self):
        if self.model_factory:
            user = AdvUserFactory()
            instance = self.model_factory()
            self.assertIsNone(instance.get_question_to_ask(user))
            for i in range(30):
                if i % 3 == 0:
                    question = QuestionFactory(content_object = instance)
                else:
                    question = QuestionFactory(content_object = ThemeFactory())
                if i % 4 == 0:
                    question.user = user
                    question.save()
                elif i % 5 == 1:
                    answer = AnswerFactory(question = question)
                    ReplyFactory(question = question, user = user, answer = answer)
            self.assertEqual(Question.objects.count(), 30)
            self.assertTrue(instance.questions.count(), 10)
            self.assertEqual(user.questions.count(), 8)
            self.assertEqual(user.replies.count(), 5)
            for i in range(10):
                question = instance.get_question_to_ask(user)
                self.assertIsNotNone(question)
                self.assertEqual(question.content_object, instance)
                self.assertNotEqual(question.user, user)
                self.assertEqual(question.replies.filter(user=user).count(), 0)

    def test_refresh_ratig(self):
        if self.model_factory:
            instance = self.model_factory()
            # no rating reports
            self.assertEqual(instance.rating, 0)
            # one rating report
            rating = RatingFactory(content_object = instance)
            instance.refresh_ratig()
            self.assertEqual(instance.rating, rating.value)
            # many rating reports
            sum = rating.value
            for i in range(20):
                if i % 2 == 0:
                    rating = RatingFactory(content_object = instance)
                    sum = sum + rating.value
                else:
                    RatingFactory(content_object = self.model_factory())
            instance.refresh_ratig()
            self.assertEqual(instance.ratings.count(), 11)
            self.assertEqual(round(instance.rating, 2), round(sum/11, 2))

class TestValidatedModelExtra(TestValidatedModel):
    absolute_url_pattern = None
    absolute_url_name = None
    model_name = None

    def test_get_absolute_url(self):
        if self.absolute_url_name and self.absolute_url_pattern:
            instance = self.model_factory()
            self.assertEqual(instance.get_absolute_url(), self.absolute_url_pattern.format(instance.pk))
            self.assertEqual(instance.get_absolute_url(), reverse('core:' + self.absolute_url_name, args=[instance.pk]))

    def test_model(self):
        if self.model_name:
            self.assertEqual(self.model_factory().model(), self.model_name)

class TestThemeModel(TestValidatedModelExtra):
    model = Theme
    model_factory = ThemeFactory
    absolute_url_pattern = '/core/themes/{}/'
    absolute_url_name = 'theme_detail'
    model_name = 'Theme'

    def test_meta_ordering(self):
        for i in range(10):
            new_theme = ThemeFactory()
        last_id = Theme.objects.last().id
        for theme in Theme.objects.all().reverse():
            self.assertEqual(theme.id, last_id)
            last_id = last_id - 1

    def test_extras(self):
        theme = ThemeFactory()
        # no creators
        self.assertIsNone(theme.extras())
        # one not validated creator
        person0 = PersonFactory()
        theme.creators.add(person0)
        self.assertEqual(theme.creators.count(), 1)
        self.assertIsNone(theme.extras())
        # one validated creator
        person1 = PersonFactory(is_validated_by_users=True)
        theme.creators.add(person1)
        self.assertEqual(theme.creators.count(), 2)
        self.assertEqual(theme.extras(), {'Создатели': '{}'.format(person1.name)})
        # two validated creators
        person2 = PersonFactory(is_validated_by_users=True)
        theme.creators.add(person2)
        self.assertEqual(theme.creators.count(), 3)
        self.assertEqual(theme.extras(), {'Создатели': '{}, {}'.format(person1.name, person2.name)})

    def test_str(self):
        theme = ThemeFactory()
        self.assertEqual(str(theme), theme.title)

    def test_favorite_count(self):
        theme = ThemeFactory()
        self.assertEqual(theme.favorite_count(), 0)
        for i in range(5):
            user = AdvUserFactory()
            theme.favorited_by.add(user)
        self.assertEqual(theme.favorited_by.count(), 5)
        self.assertEqual(theme.favorite_count(), 5)

    def test_favorite_by(self):
        user = AdvUserFactory()
        for i in range(10):
            new_theme = ThemeFactory()
            if i % 2 == 0:
                user.favorite_themes.add(new_theme)
        self.assertEqual(Theme.validation.favorite_by(user).count(), 5)

    def test_all_with_perfetch(self):
        person = PersonFactory()
        for i in range(10):
            new_theme = ThemeFactory()
            if i % 2 == 0:
                new_theme.creators.add(person)
        themes = Theme.objects.all()
        self.assertNotEqual(themes.count(), 0)
        all_with_perfetch = Theme.objects.all_with_perfetch()
        self.assertEqual(themes.count(), all_with_perfetch.count())
        for theme in themes:
            self.assertIn(theme, all_with_perfetch)
        for theme in all_with_perfetch:
            self.assertIsNotNone(theme._prefetched_objects_cache)
            if theme.creators.exists():
                self.assertIsNotNone(theme._prefetched_objects_cache['creators'])
                self.assertIn(person, theme._prefetched_objects_cache['creators'])
            else:
                for one in ['creators', 'cycles', 'books', 'movies']:
                    self.assertEqual(theme._prefetched_objects_cache[one].count(), 0)

    def test_get_question_to_ask(self):
        user = AdvUserFactory()
        theme = ThemeFactory()
        book = BookFactory()
        theme.books.add(book)
        self.assertIsNone(theme.get_question_to_ask(user))
        for i in range(30):
            if i % 3 == 0:
                question = QuestionFactory(content_object = theme)
            elif i % 3 == 1:
                question = QuestionFactory(content_object = book, theme = theme)
            else:
                question = QuestionFactory(content_object = ThemeFactory())
            if i % 4 == 0:
                question.user = user
                question.save()
            elif i % 5 == 1:
                answer = AnswerFactory(question = question)
                ReplyFactory(question = question, user = user, answer = answer)
        self.assertEqual(Question.objects.count(), 30)
        self.assertTrue(theme.questions.count(), 10)
        self.assertTrue(book.questions.count(), 10)
        self.assertTrue(theme.theme_questions.count(), 10)
        self.assertEqual(user.questions.count(), 8)
        self.assertEqual(user.replies.count(), 5)
        for i in range(10):
            question = theme.get_question_to_ask(user)
            self.assertIsNotNone(question)
            try:
                self.assertEqual(question.content_object, theme)
            except:
                self.assertEqual(question.content_object, book)
                self.assertEqual(question.theme, theme)
            self.assertNotEqual(question.user, user)
            self.assertEqual(question.replies.filter(user=user).count(), 0)

class TestPersonModel(TestValidatedModelExtra):
    model = Person
    model_factory = PersonFactory
    absolute_url_pattern = '/core/persons/{}/'
    absolute_url_name = 'person_detail'
    model_name = 'Person'

    def test_meta_ordering(self):
        letter_list = ['a', 'b', 'c', 'd', 'e']
        letter_list_copy = letter_list.copy()
        shuffle(letter_list_copy)
        for letter in letter_list_copy:
            PersonFactory(name = letter)
        i = 0
        for person in Person.objects.all():
            self.assertEqual(person.name, letter_list[i])
            i = i + 1

    def test_str(self):
        person = PersonFactory()
        self.assertEqual(str(person), person.name)

    def test_extras(self):
        person = PersonFactory()
        # no extra
        self.assertEqual(person.extras(), {'Дата рождения': None, 'Дата смерти': None})
        # with birth_date
        test_date = datetime.now()
        person = PersonFactory(born = test_date)
        self.assertEqual(person.extras(), {'Дата рождения': test_date, 'Дата смерти': None})
        # with death date
        person = PersonFactory(died = test_date)
        self.assertEqual(person.extras(), {'Дата рождения': None, 'Дата смерти': test_date})
        # for fictional person
        person = PersonFactory(is_fictional = True)
        self.assertEqual(person.extras(), {'Дата рождения': None, 'Дата смерти': None, 'Вымышленный персонаж': 'Да'})
        # all at once
        person = PersonFactory(born = test_date, died = test_date, is_fictional = True)
        self.assertEqual(person.extras(), {'Дата рождения': test_date, 'Дата смерти': test_date, 'Вымышленный персонаж': 'Да'})

    def test_passed_annotation(self):
        for i in range(30):
            instance = self.model_factory(is_validated_by_staff=(i%3==0), is_validated_by_users=(i%3==1))
        passed = Person.validation.passed()
        self.assertEqual(passed.count(), 20)
        for instance in Person.validation.passed():
            self.assertIn('title', vars(instance))
            self.assertIn('year', vars(instance))
            self.assertEqual(instance.title, instance.name)
            self.assertEqual(instance.year, instance.born)

    def test_all_with_perfetch(self):
        theme = ThemeFactory()
        for i in range(10):
            new_person = PersonFactory()
            if i % 2 == 0:
                theme.creators.add(new_person)
        all = Person.objects.all()
        all_with_perfetch = Person.objects.all_with_perfetch()
        self.assertNotEqual(all.count(), 0)
        self.assertEqual(all.count(), all_with_perfetch.count())
        for person in all:
            self.assertIn(person, all_with_perfetch)
        for person in all_with_perfetch:
            self.assertIsNotNone(person._prefetched_objects_cache)
            if person.created.exists():
                self.assertIsNotNone(person._prefetched_objects_cache['created'])
                self.assertIn(theme, person._prefetched_objects_cache['created'])
            else:
                for one in ['directed', 'wrote', 'roles', 'created', 'written_books', 'character_set', 'acted_by']:
                    self.assertEqual(person._prefetched_objects_cache[one].count(), 0)

class TestBookModel(TestValidatedModelExtra):
    model = Book
    model_factory = BookFactory
    absolute_url_pattern = '/core/books/{}/'
    absolute_url_name = 'book_detail'
    model_name = 'Book'

    def test_meta_ordering(self):
        letter_list = ['a', 'b', 'c', 'd', 'e']
        letter_list_copy = letter_list.copy()
        shuffle(letter_list_copy)
        for letter in letter_list_copy:
            BookFactory(title = letter)
        i = 0
        for book in Book.objects.all():
            self.assertEqual(book.title, letter_list[i])
            i = i + 1

    def test_str(self):
        # no etxras
        book = BookFactory()
        self.assertEqual(str(book), book.title)
        # if year
        book = BookFactory(year = 2019)
        self.assertEqual(str(book), '{} ({})'.format(book.title, book.year))

    def test_extras(self):
        # no etxras
        book = BookFactory()
        self.assertEqual(book.extras(), {'Жанр': None})
        # with genre
        book = BookFactory(genre = 1)
        self.assertEqual(book.extras(), {'Жанр': 'Фантастика'})
        # with not validated author
        person = PersonFactory()
        book = BookFactory(author = person)
        self.assertEqual(book.author, person)
        self.assertEqual(book.extras(), {'Жанр': None})
        # with validated author
        person = PersonFactory(is_validated_by_staff = True)
        book = BookFactory(author = person)
        self.assertEqual(book.author, person)
        self.assertEqual(book.extras(), {'Жанр': None, 'Автор': book.author})
        # all at once
        person = PersonFactory(is_validated_by_staff = True)
        book = BookFactory(genre = 1, author = person)
        self.assertEqual(book.author, person)
        self.assertEqual(book.extras(), {'Жанр': 'Фантастика', 'Автор': book.author})

    def test_all_with_perfetch(self):
        person = PersonFactory()
        for i in range(10):
            new_book = BookFactory()
            if i % 2 == 0:
                person.written_books.add(new_book)
        all = Book.objects.all()
        all_with_perfetch = Book.objects.all_with_perfetch()
        self.assertNotEqual(all.count(), 0)
        self.assertEqual(all.count(), all_with_perfetch.count())
        for book in all:
            self.assertIn(book, all_with_perfetch)
        for book in all_with_perfetch:
            self.assertIsNotNone(book._prefetched_objects_cache)
            for one in ['characters', 'number_set']:
                self.assertEqual(book._prefetched_objects_cache[one].count(), 0)
            if book.author:
                self.assertIsNotNone(book._state.fields_cache['author'])
                self.assertEqual(person, book._state.fields_cache['author'])
            else:
                self.assertIsNone(book._state.fields_cache['author'])

class TestMovieModel(TestValidatedModelExtra):
    model = Movie
    model_factory = MovieFactory
    absolute_url_pattern = '/core/movies/{}/'
    absolute_url_name = 'movie_detail'
    model_name = 'Movie'

    def test_meta_ordering(self):
        letter_list = ['a', 'b', 'c', 'd', 'e']
        letter_list_copy = letter_list.copy()
        shuffle(letter_list_copy)
        for letter in letter_list_copy:
            MovieFactory(title = letter)
        i = 0
        for movie in Movie.objects.all():
            self.assertEqual(movie.title, letter_list[i])
            i = i + 1

    def test_str(self):
        # no etxras
        movie = MovieFactory()
        self.assertEqual(str(movie), movie.title)
        # if year
        movie = MovieFactory(year = 2019)
        self.assertEqual(str(movie), '{} ({})'.format(movie.title, movie.year))

    def test_extras(self):
        # no etxras
        movie = MovieFactory()
        self.assertEqual(movie.extras(), {'Жанр': None})
        # with genre
        movie = MovieFactory(genre = 1)
        self.assertEqual(movie.extras(), {'Жанр': 'Фантастика'})
        # with not validated director
        person = PersonFactory()
        movie = MovieFactory(director = person)
        self.assertEqual(movie.director, person)
        self.assertEqual(movie.extras(), {'Жанр': None})
        # with validated director
        person = PersonFactory(is_validated_by_staff = True)
        movie = MovieFactory(director = person)
        self.assertEqual(movie.director, person)
        self.assertEqual(movie.extras(), {'Жанр': None, 'Режисер': movie.director})
        # with validated writer
        person = PersonFactory(is_validated_by_staff = True)
        movie = MovieFactory(writer = person)
        self.assertEqual(movie.writer, person)
        self.assertEqual(movie.extras(), {'Жанр': None, 'Сценарист': movie.writer})
        # all at once
        person = PersonFactory(is_validated_by_staff = True)
        movie = MovieFactory(genre = 1, director = person, writer = person)
        self.assertEqual(movie.director, person)
        self.assertEqual(movie.writer, person)
        self.assertEqual(movie.extras(), {'Жанр': 'Фантастика', 'Режисер': movie.director, 'Сценарист': movie.writer})

    def test_all_with_perfetch(self):
        person = PersonFactory()
        for i in range(10):
            new_movie = MovieFactory()
            if i % 2 == 0:
                person.directed.add(new_movie)
        all = Movie.objects.all()
        all_with_perfetch = Movie.objects.all_with_perfetch()
        self.assertNotEqual(all.count(), 0)
        self.assertEqual(all.count(), all_with_perfetch.count())
        for movie in all:
            self.assertIn(movie, all_with_perfetch)
        for movie in all_with_perfetch:
            self.assertIsNotNone(movie._prefetched_objects_cache)
            for one in ['roles', 'number_set']:
                self.assertEqual(movie._prefetched_objects_cache[one].count(), 0)
            if movie.director:
                self.assertIsNotNone(movie._state.fields_cache['director'])
                self.assertEqual(person, movie._state.fields_cache['director'])
            else:
                self.assertIsNone(movie._state.fields_cache['director'])
