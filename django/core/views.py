from django.views.generic import ListView, DetailView, CreateView, RedirectView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import *
from core.forms import *
from core.mixins import *

from img.forms import ImageForm

# base representaion of models
class ThemeList(OrderingMultipleObjectMixin, ListView):
    model = Theme

class ThemeDetail(ExtraContextSingleObjectMixin, DetailView):
    queryset = Theme.objects.all_with_perfetch()

class BookList(OrderingMultipleObjectMixin, ListView):
    model = Book

class BookDetail(ExtraContextSingleObjectMixin, DetailView):
    queryset = Book.objects.all_with_perfetch()

class MovieList(OrderingMultipleObjectMixin, ListView):
    model = Movie

class MovieDetail(ExtraContextSingleObjectMixin, DetailView):
    queryset = Movie.objects.all_with_perfetch()

class PersonList(OrderingMultipleObjectMixin, ListView):
    model = Person

class PersonDetail(ExtraContextSingleObjectMixin, DetailView):
    queryset = Person.objects.all_with_perfetch()

class CycleDetail(DetailView):
    queryset = Cycle.objects.all_with_perfetch()

# Creation with forms
@login_required
def theme_create(request):
    form = ThemeAutoLookupForm(initial={'created_by_user_id': request.user.id})
    image_form = ImageForm()
    if request.method == 'POST':
        form = ThemeAutoLookupForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            ImageForm().cover_processing(request, 'Theme', new_object.id)
            return redirect(new_object.get_absolute_url())
        else:
            form = ThemeAutoLookupForm(request.POST, initial={'created_by_user_id': request.user.id})
    return render(request, 'core/theme_create.html', {'form': form, 'image_form': image_form})

@login_required
def book_create(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    form = BookAutoLookupForm(initial={'created_by_user_id': request.user.id})
    image_form = ImageForm()
    cycles = theme.cycles.all()
    cycle = None
    if request.method == 'POST':
        form = BookAutoLookupForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            theme.books.add(new_object)
            ImageForm().cover_processing(request, 'Book', new_object.id)
            number = form.cleaned_data.get('number')
            if number and str(number).isdigit():
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
    context = {'form': form, 'image_form': image_form, 'cycles': cycles}
    return render(request, 'core/book_and_movie_create.html', context)

@login_required
def movie_create(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    form = MovieAutoLookupForm(initial={'created_by_user_id': request.user.id})
    image_form = ImageForm()
    cycles = theme.cycles.all()
    cycle = None
    if request.method == 'POST':
        form = MovieAutoLookupForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            theme.movies.add(new_object)
            ImageForm().cover_processing(request, 'Movie', new_object.id)
            number = form.cleaned_data.get('number')
            if number and str(number).isdigit():
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
    context = {'form': form, 'image_form': image_form, 'cycles': cycles}
    return render(request, 'core/book_and_movie_create.html', context)

@login_required
def person_create(request, related_name, pk):
    new_object = PersonForm().self_processing(request, related_name, pk)
    if isinstance(new_object, Person):
        ImageForm().cover_processing(request, 'Person', new_object.id)
        return redirect(new_object.get_absolute_url())
    form = new_object
    image_form = ImageForm()
    return render(request, 'core/person_create.html', {'form': form, 'image_form': image_form})

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
    if 'model' in request.POST:
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
    dict = {
        'Темы': Theme.validation.user_created(user_id),
        'Книги': Book.validation.user_created(user_id),
        'Фильмы': Movie.validation.user_created(user_id),
        'Люди': Person.validation.user_created(user_id),
    }
    created_by_user_dict = {}
    for key in dict.keys():
        if dict[key]:
            created_by_user_dict.update({key: dict[key]})
    return render(request, 'core/created_by_user.html', {'created_by_user_dict': created_by_user_dict})

# favorite_themes
class FavouriteThemeList(ThemeList):
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        model = self.model
        qs = model.validation.favorite_by(user)
        order = self.get_order()
        ordering_dict = {
            "alphabet_incr": qs.order_by('title'),
            "alphabet_decr": qs.order_by('-title'),
            "year_incr": qs.order_by('year'),
            "yaer_decr": qs.order_by('-year'),
            "rate_incr": qs.order_by('rating'),
            "rate_decr": qs.order_by('-rating'),
            "validated_incr": qs.order_by('validated'),
            "validated_decr": qs.order_by('-validated'),
        }
        qs = ordering_dict[order]
        return qs

@login_required()
def favorite(request, pk):
    user = request.user
    theme = get_object_or_404(Theme, pk=pk)
    if theme in user.favorite_themes.all():
        user.favorite_themes.remove(theme)
    else:
        request.user.favorite_themes.add(theme)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# raitings
@require_POST
@login_required()
def rate(request):
    model = apps.get_model(app_label='core', model_name=request.POST.get('model'), require_ready=True)
    object = get_object_or_404(model, pk=request.POST.get('object_id'))
    user = request.user
    value = int(request.POST.get('value'))
    rating = object.ratings.filter(user_rated=user)
    if rating.exists():
        rating = rating.get()
        rating.value = value
        rating.save()
    else:
        user.ratings.create(value=value, content_object=object)
    object.refresh_ratig()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# questions
@login_required
@require_POST
def create_question(request):
    model = apps.get_model(app_label='core', model_name=request.POST.get('model'), require_ready=True)
    object = get_object_or_404(model, id=request.POST.get('object_id'))
    text = request.POST.get('question_text')
    if text and text != '':
        new_question = object.questions.create(text=text, user=request.user)
        if isinstance(object, Theme):
            new_question.theme = object
            new_question.save()
        elif isinstance(object, Book) or isinstance(object, Movie):
            for theme in object.theme_set.all():
                new_question.theme = theme
            new_question.save()
        return redirect('core:add_answers', pk=new_question.pk)
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def add_answers(request, pk):
    question = get_object_or_404(Question, pk=pk)
    AnswerFormset = inlineformset_factory(Question, Answer, form=AnswerForm, formset=AnswerBaseFormSet, extra=4, can_delete=False)
    formset = AnswerFormset(instance=question)
    if 'add' in request.POST:
        formset = AnswerFormset(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            explanation = request.POST.get('explanation')
            if explanation and explanation != 0:
                question.explanation = explanation
                question.save()
            return redirect('core:question_detail', pk=pk)
    context = {'formset': formset}
    return render(request, 'questions/add_answers.html', context)

class QuestionDetail(DetailView):
    model = Question
    template_name = 'questions/question_datail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        object = self.object
        reply = object.replies.filter(user=user)
        if reply.exists():
            context.update({'user_answer': reply.first().answer})
        if user.is_authenticated:
            user_is_creator = (user == object.user)
            if user_is_creator:
                context.update({'user_is_creator': True})
            else:
                user_rating = object.ratings.filter(user_rated=user)
                if user_rating.exists():
                    context.update({'current_user_rating': user_rating.get().value})
        return context

@login_required
@require_POST
def ask_question(request):
    model = apps.get_model(app_label='core', model_name=request.POST.get('model'), require_ready=True)
    object = get_object_or_404(model, pk=request.POST.get('object_id'))
    question = object.get_question_to_ask(request.user)
    return render(request, 'questions/ask.html', {'question': question})

@login_required
def ask_similar_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    object = question.content_object
    question = object.get_question_to_ask(request.user)
    return render(request, 'questions/ask.html', {'question': question})

@login_required
def ask_random_question(request):
    question = Question.objects.get_random_question(request.user)
    return render(request, 'questions/ask.html', {'question': question})

def ask_wellcome_question(request):
    question = Question.objects.get_wellcome_question()
    return render(request, 'questions/ask.html', {'question': question})

@require_POST
def check_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    checked_answer = request.POST.get('checked_answer')
    if checked_answer:
        checked_answer = get_object_or_404(Answer, pk=checked_answer)
    if checked_answer in question.answers.all():
        user = request.user
        if user.is_authenticated:
            reply = user.replies.create(
                question = question,
                answer = checked_answer,
                outcome = checked_answer.is_right,
                points = checked_answer.points(),
            )
            return redirect('core:reply_detail', pk=reply.id)
        else:
            context = {'question': question, 'answer': checked_answer}
            return render(request, 'questions/wellcome_question_reply.html', context)
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class UserReplyRecordDetailView(DetailView):
    model = UserReplyRecord
    template_name = 'questions/reply_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        question = self.object.question
        if user.is_authenticated:
            user_rating = question.ratings.filter(user_rated=user)
            if user_rating.exists():
                context.update({'current_user_rating': user_rating.get().value})
        return context

@login_required
def get_answer(request, pk):
    reply = get_object_or_404(UserReplyRecord, pk=pk)
    question = reply.question
    return redirect('core:question_detail', pk=question.pk)

class UserCreatedQuestionsListView(ListView):
    template_name = 'questions/created_by_user.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        qs = Question.objects.user_created(user)
        return qs

# user ratings
class UserListView(ListView):
    template_name = 'ratings/users.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        user_model = get_user_model()
        qs = user_model.objects.get_points_rating_queryset()
        return qs

    def get_paginate_by(self, *args, **kwargs):
        paginate_by = self.request.GET.get('paginate_by')
        if not paginate_by:
            return self.paginate_by
        return int(paginate_by)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        paginate_by = self.get_paginate_by()
        page_suffix = '&paginate_by={}'.format(paginate_by)
        context.update({
            'paginate_by': paginate_by,
            'pagination_list': [10, 20, 30],
            'page_suffix': page_suffix,
        })
        return context

class MainPageRedirectView(RedirectView):
    def get_redirect_url(self):
        user = self.request.user
        if user.is_authenticated:
            return reverse('core:theme_list')
        else:
            return reverse('core:ask_wellcome_question')
