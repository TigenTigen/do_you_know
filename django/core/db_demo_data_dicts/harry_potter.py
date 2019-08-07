DEMO_THEMES = {
    'theme1': {
        'title': 'Гарри Поттер',
        'description': 'Мир магии и волшебства',
        'cycles': {
            'cycle1': {
                'title': 'Цикл книг о Гарри Поттере',
                'description': 'Оригинальный цикл из семи книг о Гарри Поттере',
                'books': {
                    'book1': {
                        'number': 1,
                        'title': 'Гарри Поттер и Филосовский камень', 'genre': 0, 'year': '1997',
                    },
                    'book2': {
                        'number': 2,
                        'title': 'Гарри Поттер и Тайная Комната', 'genre': 0, 'year': '1998',
                    },
                    'book3': {
                        'number': 3,
                        'title': 'Гарри Поттер и Узник Азкабана', 'genre': 0, 'year': '1999',
                    },
                    'book4': {
                        'number': 4,
                        'title': 'Гарри Поттер и Кубок Огня', 'genre': 0, 'year': '2000',
                    },
                    'book5': {
                        'number': 5,
                        'title': 'Гарри Поттер и Орден Феникса', 'genre': 0, 'year': '2003',
                    },
                    'book6': {
                        'number': 6,
                        'title': 'Гарри Поттер и Принц-Полукровка', 'genre': 0, 'year': '2005',
                    },
                    'book7': {
                        'number': 7,
                        'title': 'Гарри Поттер и Дары Смерти', 'genre': 0, 'year': '2007',
                    },
                },
            },
            'cycle2': {
                'title': 'Цикл фильмов о Гарри Поттере',
                'description': 'Экранизации книг о Гарри Поттере',
                'movies': {
                    'book1': {
                        'number': 1,
                        'title': 'Гарри Поттер и Филосовский камень', 'genre': 0, 'year': '2001',
                    },
                    'book2': {
                        'number': 2,
                        'title': 'Гарри Поттер и Тайная Комната', 'genre': 0, 'year': '2002',
                    },
                    'book3': {
                        'number': 3,
                        'title': 'Гарри Поттер и Узник Азкабана', 'genre': 0, 'year': '2004',
                    },
                    'book4': {
                        'number': 4,
                        'title': 'Гарри Поттер и Кубок Огня', 'genre': 0, 'year': '2005',
                    },
                    'book5': {
                        'number': 5,
                        'title': 'Гарри Поттер и Орден Феникса', 'genre': 0, 'year': '2007',
                    },
                    'book6': {
                        'number': 6,
                        'title': 'Гарри Поттер и Принц-Полукровка', 'genre': 0, 'year': '2009',
                    },
                    'book7': {
                        'number': 7,
                        'title': 'Гарри Поттер и Дары Смерти (часть 1)', 'genre': 0, 'year': '2010',
                    },
                    'book8': {
                        'number': 8,
                        'title': 'Гарри Поттер и Дары Смерти (часть 2)', 'genre': 0, 'year': '2011',
                    },
                },
            },
        },
    },
}

DEMO_PERSON_DEPENDENCES = {
    'person0': {
        'name': 'Джоан Роулинг',
        'born': '1965-07-31',
        'description': 'британская писательница, известная под псевдонимами Дж.К.Роулинг и Роберт Гэлбрейт',
        'created_themes': ["Гарри Поттер"],
        'written_books': ["Гарри Поттер и Филосовский камень", "Гарри Поттер и Тайная Комната", "Гарри Поттер и Узник Азкабана", "Гарри Поттер и Орден Феникса", "Гарри Поттер и Принц-Полукровка", "Гарри Поттер и Кубок Огня", "Гарри Поттер и Дары Смерти"],
        },
    'person1': {
        'name': 'Дэниел Редклиф',
        'born': '1989-07-23',
    },
    'person2': {
        'name': 'Гарри Поттер',
        'born': '1980-07-31',
        'is_fictional': True,
        'description': 'Мальчик, который выжил',
        'book_appearances': {
            'Гарри Поттер и Филосовский камень': {'is_main': True},
            'Гарри Поттер и Тайная Комната': {'is_main': True},
            'Гарри Поттер и Узник Азкабана': {'is_main': True},
            'Гарри Поттер и Орден Феникса': {'is_main': True},
            'Гарри Поттер и Принц-Полукровка': {'is_main': True},
            'Гарри Поттер и Кубок Огня': {'is_main': True},
            'Гарри Поттер и Дары Смерти': {'is_main': True},
        },
        'movie_appearences': {
            'Гарри Поттер и Филосовский камень': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Тайная Комната': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Узник Азкабана': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Орден Феникса': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Принц-Полукровка': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Кубок Огня': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Дары Смерти (часть 1)': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
            'Гарри Поттер и Дары Смерти (часть 2)': {'acter_name': 'Дэниел Редклиф', 'is_main': True},
        },
    },
    'person3': {
        'name': 'Руперт Гринт',
        'born': '1988-08-24',
    },
    'person4': {
        'name': 'Рон Уизли',
        'born': '1980-03-01',
        'is_fictional': True,
        'description': 'Лучший друг Гарри Поттера',
        'book_appearances': {
            'Гарри Поттер и Филосовский камень': {},
            'Гарри Поттер и Тайная Комната': {},
            'Гарри Поттер и Узник Азкабана': {},
            'Гарри Поттер и Орден Феникса': {},
            'Гарри Поттер и Принц-Полукровка': {},
            'Гарри Поттер и Кубок Огня': {},
            'Гарри Поттер и Дары Смерти': {},
        },
        'movie_appearences': {
            'Гарри Поттер и Филосовский камень': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Тайная Комната': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Узник Азкабана': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Орден Феникса': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Принц-Полукровка': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Кубок Огня': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Дары Смерти (часть 1)': {'acter_name': 'Руперт Гринт'},
            'Гарри Поттер и Дары Смерти (часть 2)': {'acter_name': 'Руперт Гринт'},
        },
    },
    'person5': {
        'name': 'Эмма Уотсон',
        'born': '1990-04-15',
    },
    'person6': {
        'name': 'Гермиона Грейнджер',
        'born': '1979-09-19',
        'is_fictional': True,
        'description': 'Подруга Гарри Поттера и Рона Уизли',
        'book_appearances': {
            'Гарри Поттер и Филосовский камень': {},
            'Гарри Поттер и Тайная Комната': {},
            'Гарри Поттер и Узник Азкабана': {},
            'Гарри Поттер и Орден Феникса': {},
            'Гарри Поттер и Принц-Полукровка': {},
            'Гарри Поттер и Кубок Огня': {},
            'Гарри Поттер и Дары Смерти': {},
        },
        'movie_appearences': {
            'Гарри Поттер и Филосовский камень': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Тайная Комната': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Узник Азкабана': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Орден Феникса': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Принц-Полукровка': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Кубок Огня': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Дары Смерти (часть 1)': {'acter_name': 'Эмма Уотсон'},
            'Гарри Поттер и Дары Смерти (часть 2)': {'acter_name': 'Эмма Уотсон'},
        },
    },
}

DEMO_QUESTIONS = {
    'movie_questions': {
        'Гарри Поттер и Филосовский камень': {
            'question_text': 'Сколько Мародеров появилось в фильме Гарри Поттер и Филосовский Камень?',
            'answers': (1, 2, 3, 4),
            'right_answer_number': 0,
        },
        'Гарри Поттер и Орден Феникса': {
            'question_text': 'По какому адресу располагалась штаб-квартира ордена Феникса в одноименном фильме?',
            'answers': ("Гриммо, 17", "Гриммо, 12", "Гриммо, 13", "Гриммо, 19"),
            'right_answer_number': 1,
        },
        'Гарри Поттер и Тайная Комната': {
            'question_text': 'Какой монстр скрывался в Тайной комнате на протяжении веков?',
            'answers': ("Феникс", "Василиск", "Волан-де-Морт", "Долорес Амбридж"),
            'right_answer_number': 1,
        },
    },
    'book_questions': {
        'Гарри Поттер и Филосовский Камень': {
            'question_text': 'Сколько длится обучение в Хогвартсе?',
            'answers': ("6 лет", "7 лет", "8 лет", "9 лет"),
            'right_answer_number': 1,
        },
        'Гарри Поттер и Узник Азкабана': {
            'question_text': 'Кто подарил Гарри его самую дорогу метлу?',
            'answers': ("Макгонагал", "Блек", "Дамблдор", "Люпин"),
            'right_answer_number': 1,
        },
        'Гарри Поттер и Орден Феникса': {
            'question_text': 'Кто предал Отряд Дамблдора? ',
            'answers': ("Чжоу Чанг", "Милисента Булстрот", "Мариэтта Эджком", "Сьюзен Боулз"),
            'right_answer_number': 2,
        },
    },
    'preson_questions': {
        'Эмма Уотсон': {
            'question_text': 'В какой стране родилась Эмма Уотсон',
            'answers': ("Англия", "Ирландия", "Франция", "Германия"),
            'right_answer_number': 2,
        },
        'Гарри Поттер': {
            'question_text': 'Какой из даров Смерти Гарри добыл самым первым?',
            'answers': ("Бузиная палочка", "Воскрешаюший камень", "Омут памяти", "Мантия-невидимка"),
            'right_answer_number': 3,
        },
        'Гермиона Грейнджер': {
            'question_text': 'Кем по профессии были родители Гермионы Грейнджер?',
            'answers': ("Учители", "Стоматологи", "Врачи", "Бухгалтеры"),
            'right_answer_number': 1,
        },
    },
}

DEMO_IMAGES_URL = {
    'themes_images': {
        'Гарри Поттер': "https://www.logolynx.com/images/logolynx/51/518163e837a726e58cb3b182a96f9f0d.jpeg",
    },
    'book_images': {
        'Гарри Поттер и Филосовский камень': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg/220px-Harry_Potter_and_the_Philosopher%27s_Stone_Book_Cover.jpg',
        'Гарри Поттер и Тайная Комната': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5c/Harry_Potter_and_the_Chamber_of_Secrets.jpg/220px-Harry_Potter_and_the_Chamber_of_Secrets.jpg',
        'Гарри Поттер и Узник Азкабана': 'https://upload.wikimedia.org/wikipedia/en/a/a0/Harry_Potter_and_the_Prisoner_of_Azkaban.jpg',
        'Гарри Поттер и Орден Феникса': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/70/Harry_Potter_and_the_Order_of_the_Phoenix.jpg/220px-Harry_Potter_and_the_Order_of_the_Phoenix.jpg',
        'Гарри Поттер и Принц-Полукровка': 'https://upload.wikimedia.org/wikipedia/en/f/f0/Harry_Potter_and_the_Half-Blood_Prince.jpg',
        'Гарри Поттер и Кубок Огня': 'https://upload.wikimedia.org/wikipedia/en/c/c7/Harry_Potter_and_the_Goblet_of_Fire.jpg',
        'Гарри Поттер и Дары Смерти': 'https://upload.wikimedia.org/wikipedia/en/a/a9/Harry_Potter_and_the_Deathly_Hallows.jpg',
    },
    'movie_images': {
        'Гарри Поттер и Филосовский камень': "https://upload.wikimedia.org/wikipedia/en/thumb/6/66/Hp1-americanposter.jpg/220px-Hp1-americanposter.jpg",
        'Гарри Поттер и Тайная Комната': "https://upload.wikimedia.org/wikipedia/ru/thumb/0/0b/Harry_Potter_and_the_Chamber_of_Secrets_%E2%80%94_movie.jpg/267px-Harry_Potter_and_the_Chamber_of_Secrets_%E2%80%94_movie.jpg",
        'Гарри Поттер и Узник Азкабана': "https://upload.wikimedia.org/wikipedia/ru/thumb/b/b2/Harry_Potter_and_the_Prisoner_of_Azkaban_%E2%80%94_movie.jpg/220px-Harry_Potter_and_the_Prisoner_of_Azkaban_%E2%80%94_movie.jpg",
        'Гарри Поттер и Орден Феникса': "https://upload.wikimedia.org/wikipedia/ru/thumb/6/60/Harry_Potter_and_the_Order_of_the_Phoenix_%E2%80%94_movie.jpg/267px-Harry_Potter_and_the_Order_of_the_Phoenix_%E2%80%94_movie.jpg",
        'Гарри Поттер и Принц-Полукровка': "https://upload.wikimedia.org/wikipedia/ru/thumb/8/82/Harry_Potter_and_the_Half-Blood_Prince_%E2%80%94_movie.jpg/267px-Harry_Potter_and_the_Half-Blood_Prince_%E2%80%94_movie.jpg",
        'Гарри Поттер и Кубок Огня': "https://upload.wikimedia.org/wikipedia/ru/thumb/4/45/Harry_Potter_and_the_Goblet_of_Fire_%E2%80%94_movie.jpg/220px-Harry_Potter_and_the_Goblet_of_Fire_%E2%80%94_movie.jpg",
        'Гарри Поттер и Дары Смерти (часть 1)': "https://upload.wikimedia.org/wikipedia/ru/thumb/9/98/Harry_Potter_and_the_Deathly_Hallows._Part_1_%E2%80%94_movie.jpg/267px-Harry_Potter_and_the_Deathly_Hallows._Part_1_%E2%80%94_movie.jpg",
        'Гарри Поттер и Дары Смерти (часть 2)': "https://upload.wikimedia.org/wikipedia/en/d/df/Harry_Potter_and_the_Deathly_Hallows_%E2%80%93_Part_2.jpg",
    },
    'person_images': {
        "Джоан Роулинг": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/J._K._Rowling_2010.jpg/267px-J._K._Rowling_2010.jpg",
        "Гарри Поттер": "https://upload.wikimedia.org/wikipedia/az/thumb/e/e9/Harri_Potter.jpg/240px-Harri_Potter.jpg",
        "Рон Уизли": "https://upload.wikimedia.org/wikipedia/ru/thumb/7/78/Grint-Weasley.jpg/222px-Grint-Weasley.jpg.png",
        "Гермиона Грейнджер": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Hermione_Granger_poster.jpg/220px-Hermione_Granger_poster.jpg",
        "Дэниел Редклиф": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Daniel_Radcliffe_in_July_2015.jpg/220px-Daniel_Radcliffe_in_July_2015.jpg",
        "Руперт Гринт": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Rupert_Grint_2011.jpg/200px-Rupert_Grint_2011.jpg",
        "Эмма Уотсон": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Emma_Watson_2013.jpg/225px-Emma_Watson_2013.jpg",
    },
}
