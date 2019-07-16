from core.models import Theme, Person, Book, Movie
import factory

class ThemeFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'title {}'.format(n))

    class Meta:
        model = Theme

class PersonFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'name {}'.format(n))

    class Meta:
        model = Person

class BookFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'title {}'.format(n))

    class Meta:
        model = Book

class MovieFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'title {}'.format(n))

    class Meta:
        model = Movie
