from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from core.models import Character, Role, Cycle, Number, Rating
from core.factories import PersonFactory, BookFactory, MovieFactory

class TestCharacterModel(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.book = BookFactory()
        self.character = Character.objects.create(character = self.person, book = self.book)

    def test_save(self):
        new_character = self.character
        self.assertIsNotNone(new_character.id)
        self.assertIsNone(new_character.description)
        self.assertFalse(new_character.is_main)
        self.assertEqual(self.person.character_set.get(), new_character)
        self.assertEqual(self.book.character_set.get(), new_character)

    def test_str(self):
        self.assertEqual(str(self.character), self.character.character.name)

    def test_get_absolute_url(self):
        self.assertEqual(self.character.get_absolute_url(), self.character.character.get_absolute_url())

class TestRoleModel(TestCase):
    def setUp(self):
        self.person1 = PersonFactory()
        self.person2 = PersonFactory()
        self.movie = MovieFactory()
        self.role = Role.objects.create(movie = self.movie, actor = self.person1, character = self.person2)

    def test_save(self):
        new_role = self.role
        self.assertIsNotNone(new_role.id)
        self.assertIsNone(new_role.description)
        self.assertFalse(new_role.is_main)
        self.assertEqual(self.person1.roles.get(), new_role)
        self.assertEqual(self.person2.acted_by.get(), new_role)
        self.assertEqual(self.movie.roles.get(), new_role)

    def test_str(self):
        self.assertEqual(str(self.role), '{} сыграл(а) {}'.format(self.role.actor.name, self.role.character.name))

class TestCycleModel(TestCase):
    def setUp(self):
        self.cycle = Cycle.objects.create(title = 'test_title')

    def test_str(self):
        self.assertEqual(str(self.cycle), self.cycle.title)

    def test_get_absolute_url(self):
        self.assertEqual(self.cycle.get_absolute_url(), '/core/cycles/{}/'.format(self.cycle.pk))
        self.assertEqual(self.cycle.get_absolute_url(), reverse('core:cycle_detail', args=[self.cycle.pk]))

    def test_all_with_perfetch(self):
        book = BookFactory()
        over_cycle = Cycle.objects.create(title = 'over_test_title')
        empty_cycle = Cycle.objects.create(title = 'empty_cycle_test_title')
        for i in range(30):
            if i % 3 == 0:
                self.cycle.number_set.create(number = i, book = book)
            else:
                over_cycle.number_set.create(number = i, book = book)
        all = Cycle.objects.all()
        all_with_perfetch = Cycle.objects.all_with_perfetch()
        self.assertEqual(all.count(), 3)
        self.assertEqual(all.count(), all_with_perfetch.count())
        self.assertCountEqual(all, all_with_perfetch)
        for cycle in all_with_perfetch:
            self.assertIsNotNone(cycle._prefetched_objects_cache)
            if cycle.number_set.exists():
                self.assertIsNotNone(cycle._prefetched_objects_cache['number_set'])
                self.assertEqual(book, cycle._prefetched_objects_cache['number_set'].first().book)
            else:
                self.assertEqual(cycle._prefetched_objects_cache['number_set'].count(), 0)

class TestNumberModel(TestCase):
    def setUp(self):
        self.cycle = Cycle.objects.create(title = 'text_title')
        self.movie = MovieFactory()
        self.book = BookFactory()

    def test_save_for_movie_cycle(self):
        movie_number = Number.objects.create(cycle = self.cycle, movie = self.movie, number = 1)
        self.assertIsNotNone(movie_number.id)
        self.assertEqual(movie_number.number, 1)
        self.assertEqual(self.cycle.number_set.get(), movie_number)
        self.assertEqual(self.movie.number_set.get(), movie_number)

    def test_save_for_book_cycle(self):
        book_number = Number.objects.create(cycle = self.cycle, book = self.book, number = 1)
        self.assertIsNotNone(book_number.id)
        self.assertEqual(book_number.number, 1)
        self.assertEqual(self.cycle.number_set.get(), book_number)
        self.assertEqual(self.book.number_set.get(), book_number)

    def test_str(self):
        movie_number = Number.objects.create(cycle = self.cycle, movie = self.movie, number = 1)
        self.assertEqual(str(movie_number), '{} #1'.format(movie_number.cycle))

    def test_get_absolute_url(self):
        movie_number = Number.objects.create(cycle = self.cycle, movie = self.movie, number = 1)
        self.assertEqual(movie_number.get_absolute_url(), movie_number.cycle.get_absolute_url())

    def test_object(self):
        # no movie, no book
        new_number = Number.objects.create(cycle = self.cycle, number = 1)
        self.assertIsNone(new_number.object())
        with self.assertRaises(ObjectDoesNotExist):
            Number.objects.get(id=new_number.id)
        # book_number
        book_number = Number.objects.create(cycle = self.cycle, book = self.book, number = 1)
        self.assertEqual(book_number.object(), self.book)
        book_number.delete()
        # movie number
        movie_number = Number.objects.create(cycle = self.cycle, movie = self.movie, number = 1)
        self.assertEqual(movie_number.object(), self.movie)
        movie_number.delete()
        # book & movie
        new_number = Number.objects.create(cycle = self.cycle, number = 1, book = self.book, movie = self.movie)
        self.assertIsNone(new_number.object())
        with self.assertRaises(ObjectDoesNotExist):
            Number.objects.get(id=new_number.id)
