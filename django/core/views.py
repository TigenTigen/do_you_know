from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.apps import apps
from django.http import HttpResponseRedirect

from core.models import *
from core.forms import *
from core.mixins import *

# base representaion of models
class ThemeList(ListView):
    queryset = Theme.validation.passed()
    paginate_by = 10

class ThemeDetail(ValidationSingleObjectMixin, DetailView):
    model = Theme

class BookList(ListView):
    queryset = Book.validation.passed()
    template_name='core/simple_list.html'
    paginate_by = 20

class BookDetail(ValidationSingleObjectMixin, DetailView):
    model = Book

class MovieList(ListView):
    queryset = Movie.validation.passed()
    template_name='core/simple_list.html'
    paginate_by = 20

class MovieDetail(ValidationSingleObjectMixin, DetailView):
    model = Movie

class PersonList(ListView):
    queryset = Person.validation.passed()
    template_name='core/simple_list.html'
    paginate_by = 20

class PersonDetail(ValidationSingleObjectMixin, DetailView):
    model = Person

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

# new objects validation
class ValidationThemeList(ValidationMultipleObjectMixin, ListView):
    model = Theme

class ValidationBookList(ValidationMultipleObjectMixin, ListView):
    model = Book

class ValidationMovieList(ValidationMultipleObjectMixin, ListView):
    model = Movie

class ValidationPersonList(ValidationMultipleObjectMixin, ListView):
    model = Person

@require_POST
@login_required()
def validation(request):
    model = apps.get_model(app_label='core', model_name=request.POST.get('model'), require_ready=True)
    object = get_object_or_404(model, pk=request.POST.get('object_id'))
    user = request.user
    if 'staff_validation' in request.POST:
        object.validated_by_staff(user)
    elif 'user_approve' in request.POST:
        object.approved(user)
    elif 'user_disapprove' in request.POST:
        object.disapproved(user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def created_by_user(request):
    user_id = request.user.id
    created_by_user_dict = {
        'Темы': Theme.validation.user_created(user_id),
        'Книги': Book.validation.user_created(user_id),
        'Фильмы': Movie.validation.user_created(user_id),
        'Люди': Person.validation.user_created(user_id),
    }
    return render(request, 'core/created_by_user.html', {'created_by_user_dict': created_by_user_dict})

# favorite_themes
class FavouriteThemeList(ListView):
    model = Theme
    template_name='core/theme_favorite_list.html'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return Theme.objects.favorite_by(user)

@login_required()
def favorite(request, pk):
    user = request.user
    theme = get_object_or_404(Theme, pk=pk)
    if theme in user.favorite_themes.all():
        user.favorite_themes.remove(theme)
    else:
        request.user.favorite_themes.add(theme)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
