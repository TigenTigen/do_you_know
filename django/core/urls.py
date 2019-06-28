from django.urls import path
from core.views import *

# comon_prefix: core/'
app_name = 'core'
urlpatterns = [
        #themes
    path('themes/', ThemeList.as_view(), name='theme_list'),
    path('themes/<int:pk>/', ThemeDetail.as_view(), name='theme_detail'),
    path('themes/create/', theme_create, name='theme_create'),
    path('themes/validation/', ValidationThemeList.as_view(), name='theme_list_validation'),
    path('themes/favorite/<int:pk>/', favorite, name='favorite'),
    path('themes/favorite/user/', FavouriteThemeList.as_view(), name='favorite_by_user'),
        #cycles
    path('cycles/<int:pk>/', CycleDetail.as_view(), name='cycle_detail'),
        #books
    path('books/', BookList.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetail.as_view(), name='book_detail'),
    path('books/create/<int:theme_id>/', book_create, name='book_create'),
    path('books/validation/', ValidationBookList.as_view(), name='book_list_validation'),
        #movies
    path('movies/', MovieList.as_view(), name='movie_list'),
    path('movies/<int:pk>/', MovieDetail.as_view(), name='movie_detail'),
    path('movies/create/<int:theme_id>/', movie_create, name='movie_create'),
    path('movies/validation/', ValidationMovieList.as_view(), name='movie_list_validation'),
        #persons
    path('persons/', PersonList.as_view(), name='person_list'),
    path('persons/<int:pk>/', PersonDetail.as_view(), name='person_detail'),
    path('persons/create/role/<int:pk>/', person_create_as_role, name='person_create_as_role'),
    path('persons/create/<str:related_name>/<int:pk>/', person_create, name='person_create'),
    path('persons/validation/', ValidationPersonList.as_view(), name='person_list_validation'),
        #validation
    path('validation/', validation, name='validation'),
    path('created_by_user/', created_by_user, name='created_by_user'),
]
