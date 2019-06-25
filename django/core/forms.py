from django import forms
from django.shortcuts import get_object_or_404
from core.models import *

# base forms
class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ('title', 'description', 'created_by_user_id')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name', 'born', 'died', 'description', 'is_fictional', 'created_by_user_id')
        widgets = {'created_by_user_id': forms.HiddenInput()}

    def self_processing(self, request, related_name, pk):
        if related_name == 'character':
            form = CharacterPersonForm()
        else:
            form = PersonForm()
        model_dict = {'creator': Theme, 'author': Book, 'character': Book, 'director': Movie, 'writer': Movie}
        superinstance = get_object_or_404(model_dict[related_name], pk=pk)
        if request.method == 'POST':
            if related_name == 'character':
                form = CharacterPersonForm(request.POST, initial={'created_by_user_id': request.user.id})
            else:
                form = PersonForm(request.POST, initial={'created_by_user_id': request.user.id})
            if form.is_valid():
                new_object = form.save()
                if related_name == 'creator':
                    superinstance.creators.add(new_object)
                elif related_name == 'author':
                    superinstance.author = new_object
                    superinstance.save()
                elif related_name == 'character':
                    Character.objects.create(character=new_object,
                                             book=superinstance,
                                             is_main=form.cleaned_data.get('is_main'),
                                             description=form.cleaned_data.get('character_description'))
                elif related_name == 'director':
                    superinstance.director = new_object
                    superinstance.save()
                elif related_name == 'writer':
                    superinstance.writer = new_object
                    superinstance.save()
                return new_object
        return form

class CharacterPersonForm(PersonForm):
    is_main = forms.BooleanField(label='Главный герой данной книги', required=False)
    character_description = forms.CharField(label='Описание героя в данной книге', required=False, widget=forms.Textarea())

    class Meta(PersonForm.Meta):
        fields = ('name', 'born', 'died', 'description', 'is_fictional', 'created_by_user_id', 'is_main', 'character_description')

class BookForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(label='Известные циклы', widget=forms.HiddenInput(), queryset=Cycle.objects.all(), required=False)
    number = forms.CharField(label='Порядковый номер в серии', required=False)

    class Meta:
        model = Book
        fields = ('title', 'year', 'genre', 'plot', 'created_by_user_id', 'cycle', 'number')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class MovieForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(label='Известные циклы', widget=forms.HiddenInput(), queryset=Cycle.objects.all(), required=False)
    number = forms.CharField(label='Порядковый номер в серии', required=False)

    class Meta:
        model = Movie
        fields = ('title', 'year', 'genre', 'plot', 'created_by_user_id', 'cycle', 'number')
        widgets = {'created_by_user_id': forms.HiddenInput()}

class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ('title', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

class NumberForm(forms.ModelForm):
    class Meta:
        model = Number
        fields = '__all__'
