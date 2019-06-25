from django.urls import path
from core.views import *

# comon_prefix: core/'
app_name = 'core'
urlpatterns = [
    path('themes/', ThemeList.as_view(), name='theme_list'),
    path('themes/<int:pk>/', ThemeDetail.as_view(), name='theme_detail'),
    path('books/', BookList.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetail.as_view(), name='book_detail'),
    path('movies/', MovieList.as_view(), name='movie_list'),
    path('movies/<int:pk>/', MovieDetail.as_view(), name='movie_detail'),
    path('persons/', PersonList.as_view(), name='person_list'),
    path('persons/<int:pk>/', PersonDetail.as_view(), name='person_detail'),
]
