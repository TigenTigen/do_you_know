from selectable.base import ModelLookup
from selectable.registry import registry

from core.models import Theme, Book, Movie, Person

class ThemeLookup(ModelLookup):
    model = Theme
    search_fields = ('title__icontains', )

class BookLookup(ModelLookup):
    model = Book
    search_fields = ('title__icontains', )

class MovieLookup(ModelLookup):
    model = Movie
    search_fields = ('title__icontains', )

class PersonLookup(ModelLookup):
    model = Person
    search_fields = ('name__icontains', )

registry.register(ThemeLookup)
registry.register(BookLookup)
registry.register(MovieLookup)
registry.register(PersonLookup)
