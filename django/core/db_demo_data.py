from core.models import *
from img.forms import ImageForm

THEMES = {
    'theme1': {
        'title': '',
        'description': '',
        'creators': {
            'person1': {
                'name': '',
                'born': '',
                'died': '',
                'description': '',
            },
        },
        'cycles': {
            'cycle1': {
                'title': '',
                'description': '',
                'books': {
                    'book1': {
                        'number': 0,
                        'title': '',
                        'description': '',
                        'genre': '',
                        'year': '',
                    },
                },
                'movies': {
                    'movie1': {
                        'number': 0,
                        'title': '',
                        'description': '',
                        'genre': '',
                        'year': '',
                    },
                },
            },
        },
        'books': {},
        'movies': {},
    },
}

PERSON_DEPENDENCES = {
    'person1': {
        'name': '',
        'born': '',
        'died': '',
        'is_fictional': True,
        'description': '',
        'created_themes': [],
        'directed_movies': [],
        'written_movies': [],
        'written_books': [],
        'book_appearances': {
            'book1_title': {
                'is_main': True,
                'description': '',
            },
        },
        'movie_appearences': {
            'movie1_title': {
                'acter_name': '',
                'is_main': True,
                'description': '',
            },
        },
    },
}

QUESTIONS = {
    'movie_questions': {
        'movie1_title': {
            'question_text': '',
            'answers': (),
            'right_answer_number': 0,
        },
    },
    'book_questions': {},
    'preson_questions': {},
}

IMAGES_URL = {
    'themes_images': {},
    'book_images': {},
    'movie_images': {},
    'person_images': {},
}

def create_person(dict, user):
    person, created = Person.objects.get_or_create(
        name = dict.get('name'),
        defaults = {
            'born': dict.get('born'),
            'died': dict.get('died'),
            'description': dict.get('description'),
            'is_fictional': dict.get('is_fictional', False),
            'created_by_user_id': user.id,
        }
    )
    if created:
        person.validated_by_staff(user)
    return person

def create_book(dict, user):
    book, created = Book.objects.get_or_create(
        title = dict.get('title'),
        defaults = {
            'description': dict.get('description'),
            'genre': dict.get('genre'),
            'year': dict.get('year'),
            'created_by_user_id': user.id,
        }
    )
    if created:
        book.validated_by_staff(user)
    return book

def create_movie(dict, user):
    movie, created = Movie.objects.get_or_create(
        title = dict.get('title'),
        defaults = {
            'description': dict.get('description'),
            'genre': dict.get('genre'),
            'year': dict.get('year'),
            'created_by_user_id': user.id,
        }
    )
    if created:
        movie.validated_by_staff(user)
    return movie

def create_question(dict, object, user):
    question, created = object.questions.get_or_create(
        text = dict.get('question_text'),
        user = user,
    )
    if not isinstance(object, Person):
        question.theme = object.theme_set.get()
        question.save()
    answer_tuple = dict.get('answers')
    right_answer = dict.get('right_answer_number')
    for i in range(len(answer_tuple)):
        answer, created = question.answers.get_or_create(text = answer_tuple[i])
        if i == right_answer:
            answer.is_right = True
            answer.save()

def download_theme_dict(dict, user):
    for theme_dickt in dict.values():
        theme, created = Theme.objects.get_or_create(
            title = theme_dickt.get('title'),
            defaults = {'description': theme_dickt.get('description'), 'created_by_user_id': user.id}
        )
        if created:
            theme.validated_by_staff(user)
        for creator_dict in theme_dickt.get('creators', {}).values():
            person = create_person(creator_dict, user)
            theme.creators.add(person)
        for cycle_dict in theme_dickt.get('cycles', {}).values():
            cycle, created = theme.cycles.get_or_create(
                title = cycle_dict.get('title'),
                defaults = {'description': cycle_dict.get('description')}
            )
            for book_dict in cycle_dict.get('books', {}).values():
                book = create_book(book_dict, user)
                theme.books.add(book)
                number, created = cycle.number_set.get_or_create(number = book_dict.get('number'), book = book)
            for movie_dict in cycle_dict.get('movies', {}).values():
                movie = create_movie(movie_dict, user)
                theme.movies.add(movie)
                number, created = cycle.number_set.get_or_create(number = movie_dict.get('number'), movie = movie)
        for book_dict in theme_dickt.get('books', {}).values():
            book = create_book(book_dict, user)
            theme.books.add(book)
        for movie_dict in theme_dickt.get('movies', {}).values():
            movie = create_movie(movie_dict, user)
            theme.movies.add(movie)

def download_person_dict(dict, user):
    for i in range(0, len(dict)+1):
        person_dict = dict.get('person' + str(i))
        if person_dict:
            person = create_person(person_dict, user)
            for theme in person_dict.get('created_themes', []):
                theme = Theme.objects.get(title__iexact=theme)
                theme.creators.add(person)
            for movie in person_dict.get('directed_movies', []):
                movie = Movie.objects.get(title__iexact=movie)
                movie.director = person
                movie.save()
            for movie in person_dict.get('written_movies', []):
                movie = Movie.objects.get(title__iexact=movie)
                movie.writer = person
                movie.save()
            for book in person_dict.get('written_books', []):
                book = Book.objects.get(title__iexact=book)
                book.author = person
                book.save()
            book_appearances_dict = person_dict.get('book_appearances')
            if book_appearances_dict:
                for key in book_appearances_dict.keys():
                    book = Book.objects.get(title__iexact = key)
                    character_dict = book_appearances_dict.get(key)
                    character, created = book.character_set.get_or_create(
                        character = person,
                        defaults = {
                            'is_main': character_dict.get('is_main', False),
                            'description': character_dict.get('description'),
                        }
                    )
            movie_appearances_dict = person_dict.get('movie_appearences')
            if movie_appearances_dict:
                for key in movie_appearances_dict.keys():
                    movie = Movie.objects.get(title__iexact = key)
                    character_dict = movie_appearances_dict.get(key)
                    role, created = movie.roles.get_or_create(
                        character = person,
                        actor = Person.objects.get(name = character_dict.get('acter_name')),
                        defaults = {
                            'is_main': character_dict.get('is_main', False),
                            'description': character_dict.get('description'),
                        }
                    )

def download_questions_dict(dict, user):
    movie_questions_dict = dict.get('movie_questions')
    if movie_questions_dict:
        for key in movie_questions_dict.keys():
            movie = Movie.objects.get(title__iexact = key)
            question_dict = movie_questions_dict.get(key)
            create_question(question_dict, movie, user)
    book_questions_dict = dict.get('book_questions')
    if book_questions_dict:
        for key in book_questions_dict.keys():
            book = Book.objects.get(title__iexact = key)
            question_dict = book_questions_dict.get(key)
            create_question(question_dict, book, user)
    person_questions_dict = dict.get('preson_questions')
    if person_questions_dict:
        for key in person_questions_dict.keys():
            person = Person.objects.get(name__iexact = key)
            question_dict = person_questions_dict.get(key)
            create_question(question_dict, person, user)

def download_image_dict(dict, user):
    theme_img_dict = dict.get('themes_images')
    if theme_img_dict:
        for key in theme_img_dict.keys():
            theme = Theme.objects.get(title__iexact = key)
            if not theme.images.exists():
                ImageForm().demo_download_processing(theme, theme_img_dict.get(key), user)
    book_img_dict = dict.get('book_images')
    if book_img_dict:
        for key in book_img_dict.keys():
            book = Book.objects.get(title__iexact = key)
            if not book.images.exists():
                ImageForm().demo_download_processing(book, book_img_dict.get(key), user)
    movie_img_dict = dict.get('movie_images')
    if movie_img_dict:
        for key in movie_img_dict.keys():
            movie = Movie.objects.get(title__iexact = key)
            if not movie.images.exists():
                ImageForm().demo_download_processing(movie, movie_img_dict.get(key), user)
    person_img_dict = dict.get('person_images')
    if person_img_dict:
        for key in person_img_dict.keys():
            person = Person.objects.get(name__iexact = key)
            if not person.images.exists():
                ImageForm().demo_download_processing(person, person_img_dict.get(key), user)

def db_demo_data(user):
    from core.db_demo_data_dicts.star_wars import DEMO_THEMES, DEMO_PERSON_DEPENDENCES, DEMO_QUESTIONS, DEMO_IMAGES_URL
    download_theme_dict(DEMO_THEMES, user)
    download_person_dict(DEMO_PERSON_DEPENDENCES, user)
    download_questions_dict(DEMO_QUESTIONS, user)
    download_image_dict(DEMO_IMAGES_URL, user)
    from core.db_demo_data_dicts.harry_potter import DEMO_THEMES, DEMO_PERSON_DEPENDENCES, DEMO_QUESTIONS, DEMO_IMAGES_URL
    download_theme_dict(DEMO_THEMES, user)
    download_person_dict(DEMO_PERSON_DEPENDENCES, user)
    download_questions_dict(DEMO_QUESTIONS, user)
    download_image_dict(DEMO_IMAGES_URL, user)
    from core.db_demo_data_dicts.game_of_thrones import DEMO_THEMES, DEMO_IMAGES_URL
    download_theme_dict(DEMO_THEMES, user)
    download_image_dict(DEMO_IMAGES_URL, user)
