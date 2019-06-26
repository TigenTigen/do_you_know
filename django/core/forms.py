from django import forms
from django.shortcuts import get_object_or_404
from selectable.forms import AutoCompleteWidget
from core.models import *
from core.lookups import *

# base forms
class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ('title', 'description', 'created_by_user_id')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class ThemeAutoLookupForm(ThemeForm):
    title = forms.CharField(
        label='Наименование',
        widget=AutoCompleteWidget(ThemeLookup, allow_new=True),
        required=True,
        max_length=100,
    )

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name', 'born', 'died', 'description', 'is_fictional', 'created_by_user_id')
        widgets = {'created_by_user_id': forms.HiddenInput()}

    def self_processing(self, request, related_name, pk):
        if related_name == 'character':
            form = CharacterPersonForm(initial={'created_by_user_id': request.user.id})
        else:
            form = PersonAutoLookupForm(initial={'created_by_user_id': request.user.id})
        model_dict = {'creator': Theme, 'author': Book, 'character': Book, 'director': Movie, 'writer': Movie}
        superinstance = get_object_or_404(model_dict[related_name], pk=pk)
        if request.method == 'POST':
            name = request.POST.get('name')
            if name != '' and name:
                person = Person.objects.filter(name=name)
                if person.exists():
                    new_object = person.get()
                else:
                    if related_name == 'character':
                        form = CharacterPersonForm(request.POST)
                    else:
                        form = PersonAutoLookupForm(request.POST)
                    if form.is_valid():
                        new_object = form.save()
                if new_object:
                    if related_name == 'creator':
                        superinstance.creators.add(new_object)
                    elif related_name == 'author':
                        superinstance.author = new_object
                        superinstance.save()
                    elif related_name == 'character':
                        Character.objects.create(character=new_object,
                                                 book=superinstance,
                                                 is_main=('is_main' in request.POST),
                                                 description=request.POST.get('character_description'))
                    elif related_name == 'director':
                        superinstance.director = new_object
                        superinstance.save()
                    elif related_name == 'writer':
                        superinstance.writer = new_object
                        superinstance.save()
                    return new_object
        return form

class PersonAutoLookupForm(PersonForm):
    name = forms.CharField(
        label='Имя',
        widget=AutoCompleteWidget(PersonLookup, allow_new=True),
        required=True,
        max_length=100,
    )

class CharacterPersonForm(PersonAutoLookupForm):
    is_main = forms.BooleanField(label='Главный герой данной книги', required=False)
    character_description = forms.CharField(label='Описание героя в данной книге', required=False, widget=forms.Textarea())

    class Meta(PersonForm.Meta):
        fields = ('name', 'born', 'died', 'description', 'is_fictional', 'created_by_user_id', 'is_main', 'character_description')

class ActorNameAutoLookupForm(forms.Form):
    actor_name = forms.CharField(
        label='Имя',
        widget=AutoCompleteWidget(PersonLookup, allow_new=True),
        required=True,
        max_length=100,
    )

class BookForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(label='Известные циклы', widget=forms.HiddenInput(), queryset=Cycle.objects.all(), required=False)
    number = forms.CharField(label='Порядковый номер в серии', required=False)

    class Meta:
        model = Book
        fields = ('title', 'year', 'genre', 'plot', 'created_by_user_id', 'cycle', 'number')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class BookAutoLookupForm(BookForm):
    title = forms.CharField(
        label='Наименование',
        widget=AutoCompleteWidget(BookLookup, allow_new=True),
        required=True,
        max_length=100,
    )

class MovieForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(label='Известные циклы', widget=forms.HiddenInput(), queryset=Cycle.objects.all(), required=False)
    number = forms.CharField(label='Порядковый номер в серии', required=False)

    class Meta:
        model = Movie
        fields = ('title', 'year', 'genre', 'plot', 'created_by_user_id', 'cycle', 'number')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class MovieAutoLookupForm(MovieForm):
    title = forms.CharField(
        label='Наименование',
        widget=AutoCompleteWidget(MovieLookup, allow_new=True),
        required=True,
        max_length=100,
    )

class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ('title', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

class NumberForm(forms.ModelForm):
    class Meta:
        model = Number
        fields = '__all__'
