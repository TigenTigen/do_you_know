from config.universal_tests import UniversalFormTest
from core.forms import BookForm, BookAutoLookupForm, MovieForm, MovieAutoLookupForm, CycleForm, NumberForm
from core.models import Book, Movie, Cycle, Number
from user.factories import AdvUserFactory

class TestBookForm(UniversalFormTest):
    form_class = BookForm
    form_model_class = Book

    def get_valid_data_dict(self):
        self.user = AdvUserFactory()
        data_dict = {'title': 'test_title', 'created_by_user_id': self.user.id}
        return data_dict

    def get_field_validation_check_dict(self):
        check_dict = {
            'title': {
                'wrong_choices': [None, '', ' '],
                'right_choices': [1, 'some string', 'some_string'],
            },
            'description': {
                'wrong_choices': [],
                'right_choices': [None, '', ' ', 1, 'some string', 'some_string'],
            },
            'number': {
                'wrong_choices': [],
                'right_choices': ['8', 1, 2, 505],
            },
        }
        return check_dict

    def test_clean_description(self):
        data_dict = self.valid_data_dict
        data_dict.update({'description': ''})
        form = self.form_class(data_dict)
        if form.is_valid():
            new_object = form.save()
            self.assertIsNone(new_object.description)
            self.green('   OK   Clean method for field description works as expected')
        else:
            self.print_invalid_form_errors(form)

    def test_clean_number(self):
        data_dict = self.valid_data_dict
        choices = [None, '', ' ', 'some string', 'some_string', -1, 66666666666666666666666, 7.77, 0]
        for choice in choices:
            data_dict.update({'number': choice})
            form = self.form_class(data_dict)
            if form.is_valid():
                self.assertIsNone(form.cleaned_data.get('nember'))
            else:
                self.print_invalid_form_errors(form)
        self.green('   OK   Clean method for field number works as expected')

class TestBookAutoLookupForm(TestBookForm):
    form_class = BookAutoLookupForm
    form_super_class = BookForm

class TestMovieForm(TestBookForm):
    form_class = MovieForm
    form_model_class = Movie

class TestMovieAutoLookupForm(TestMovieForm):
    form_class = MovieAutoLookupForm
    form_super_class = MovieForm

class TestCycleForm(UniversalFormTest):
    form_class = CycleForm
    form_model_class = Cycle
    valid_data_dict = {'title': 'test_title'}

    def get_field_validation_check_dict(self):
        check_dict = {
            'title': {
                'wrong_choices': [None, '', ' '],
                'right_choices': [1, 'some string', 'some_string'],
            },
            'description': {
                'wrong_choices': [],
                'right_choices': [None, '', ' ', 1, 'some string', 'some_string'],
            },
        }
        return check_dict

    def test_clean_description(self):
        data_dict = self.valid_data_dict
        data_dict.update({'description': ''})
        form = self.form_class(data_dict)
        if form.is_valid():
            new_object = form.save()
            self.assertIsNone(new_object.description)
            self.green('   OK   Clean method for field description works as expected')
        else:
            self.print_invalid_form_errors(form)

class TestNumberForm(UniversalFormTest):
    form_class = NumberForm
    form_model_class = Number
