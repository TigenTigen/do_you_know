import django
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, redirect
from django.urls import reverse
from core.models import *

class ThemeList(ListView):
    model = Theme
    paginate_by = 10

class ThemeDetail(DetailView):
    queryset = Theme.objects.all_with_perfetch()

class BookList(ListView):
    model = Book
    template_name='core/simple_list.html'
    paginate_by = 20

class BookDetail(DetailView):
    queryset = Book.objects.all_with_perfetch()

class MovieList(ListView):
    model = Movie
    template_name='core/simple_list.html'
    paginate_by = 20

class MovieDetail(DetailView):
    queryset = Movie.objects.all_with_perfetch()

class PersonList(ListView):
    model = Person
    template_name='core/simple_list.html'
    paginate_by = 20

class PersonDetail(DetailView):
    queryset = Person.objects.all_with_perfetch()
