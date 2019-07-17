from core.models import *
from user.factories import AdvUserFactory
import factory
import factory.fuzzy

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

class QuestionFactory(factory.DjangoModelFactory):
    text = factory.Sequence(lambda n: 'text {}'.format(n))
    user = factory.SubFactory(AdvUserFactory)

    class Meta:
        model = Question

class AnswerFactory(factory.DjangoModelFactory):
    text = factory.Sequence(lambda n: 'text {}'.format(n))

    class Meta:
        model = Answer

class ReplyFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(AdvUserFactory)

    class Meta:
        model = UserReplyRecord

class RatingFactory(factory.DjangoModelFactory):
    user_rated = factory.SubFactory(AdvUserFactory)
    value = factory.fuzzy.FuzzyInteger(1, 5)

    class Meta:
        model = Rating
