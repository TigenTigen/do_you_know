import django
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from core.forms import *
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

class CycleDetail(DetailView):
    queryset = Cycle.objects.all_with_perfetch()

# Creation with forms
@login_required
def theme_create(request):
    form = ThemeAutoLookupForm(initial={'created_by_user_id': request.user.id})
    if request.method == 'POST':
        form = ThemeAutoLookupForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            return redirect(new_object.get_absolute_url())
    return render(request, 'core/theme_create.html', {'form': form})

@login_required
def book_create(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    form = BookAutoLookupForm(initial={'created_by_user_id': request.user.id})
    cycles = theme.cycles.all()
    cycle = None
    if request.method == 'POST':
        form = BookAutoLookupForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            theme.books.add(new_object)
            number = form.cleaned_data.get('number')
            if number.isdigit():
                new_cycle_title = request.POST.get('new_cycle_title')
                if new_cycle_title and new_cycle_title != '':
                    form_dict = {'title': new_cycle_title, 'description': request.POST.get('new_cycle_description')}
                    cycle_form = CycleForm(form_dict)
                    if cycle_form.is_valid():
                        cycle = cycle_form.save()
                elif 'cycle' in request.POST:
                    cycle_id = request.POST.get('cycle')
                    if cycle_id and cycle_id.isdigit():
                        cycle = cycles.get(id=int(cycle_id))
                if cycle:
                    form_dict = {'number': int(number), 'cycle': cycle.id, 'book': new_object.id}
                    number_form = NumberForm(form_dict)
                    if number_form.is_valid():
                        number_form.save()
                        if not cycle in cycles:
                            theme.cycles.add(cycle)
            return redirect(new_object.get_absolute_url())
    context = {'form': form, 'cycles': cycles}
    return render(request, 'core/book_and_movie_create.html', context)

@login_required
def movie_create(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    form = MovieAutoLookupForm(initial={'created_by_user_id': request.user.id})
    cycles = theme.cycles.all()
    cycle = None
    if request.method == 'POST':
        form = MovieAutoLookupForm()
        if form.is_valid():
            new_object = form.save()
            theme.movies.add(new_object)
            number = form.cleaned_data.get('number')
            if number.isdigit():
                new_cycle_title = request.POST.get('new_cycle_title')
                if new_cycle_title and new_cycle_title != '':
                    form_dict = {'title': new_cycle_title, 'description': request.POST.get('new_cycle_description')}
                    cycle_form = CycleForm(form_dict)
                    if cycle_form.is_valid():
                        cycle = cycle_form.save()
                elif 'cycle' in request.POST:
                    cycle_id = request.POST.get('cycle')
                    if cycle_id and cycle_id.isdigit():
                        cycle = cycles.get(id=int(cycle_id))
                if cycle:
                    form_dict = {'number': int(number), 'cycle': cycle.id, 'movie': new_object.id}
                    number_form = NumberForm(form_dict)
                    if number_form.is_valid():
                        number_form.save()
                        if not cycle in cycles:
                            theme.cycles.add(cycle)
            return redirect(new_object.get_absolute_url())
    context = {'form': form, 'cycles': cycles}
    return render(request, 'core/book_and_movie_create.html', context)

@login_required
def person_create(request, related_name, pk):
    new_object = PersonForm().self_processing(request, related_name, pk)
    if isinstance(new_object, Person):
        return redirect(new_object.get_absolute_url())
    form = new_object
    return render(request, 'core/person_create.html', {'form': form})

@login_required
def person_create_as_role(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    actor_name_field = ActorNameAutoLookupForm()
    character_form = CharacterPersonForm(initial={'created_by_user_id': request.user.id})
    character, actor = None, None
    if request.method == 'POST':
        character_name = request.POST.get('name')
        if character_name != '' and character_name:
            person = Person.objects.filter(name=character_name)
            if person.exists():
                character = person.get()
            else:
                character_form = CharacterPersonForm(request.POST)
                if character_form.is_valid():
                    character = character_form.save()
        if character:
            actor_name = request.POST.get('actor_name')
            if actor_name != '' and actor_name:
                person = Person.objects.filter(name=actor_name)
                if person.exists():
                    actor = person.get()
                else:
                    actor_form_dict = {
                        'name': request.POST.get('actor_name'),
                        'born': request.POST.get('actor_born'),
                        'died': request.POST.get('actor_died'),
                        'description': request.POST.get('actor_description'),
                        'created_by_user_id': request.user.id,
                    }
                    actor_form = PersonForm(actor_form_dict)
                    if actor_form.is_valid():
                        actor = actor_form.save()
            if actor:
                Role.objects.create(actor=actor,
                                    character=character,
                                    movie=movie,
                                    is_main=('is_main' in request.POST),
                                    description=request.POST.get('character_description'))
        return redirect('core:movie_detail', pk=pk)
    context = {'actor_name_field': actor_name_field, 'character_form': character_form}
    return render(request, 'core/person_create_as_role.html', context)
