from config.universal_tests import UniversalFormTest
from core.models import Person
from core.forms import PersonForm, PersonAutoLookupForm, CharacterPersonForm, ActorNameAutoLookupForm
from user.factories import AdvUserFactory

class TestPersonForm(UniversalFormTest):
    form_class = PersonForm
    form_model_class = Person

    def get_valid_data_dict(self):
        self.user = AdvUserFactory()
        data_dict = {'name': 'test_name', 'created_by_user_id': self.user.id}
        return data_dict

    def get_field_validation_check_dict(self):
        check_dict = {
            'name': {
                'wrong_choices': [None, '', ' '],
                'right_choices': [1, 'some string', 'some_string'],
            },
            'description': {
                'wrong_choices': [],
                'right_choices': [None, '', ' ', 1, 'some string', 'some_string'],
            },
            'created_by_user_id': {
                'wrong_choices': [None, '', ' ', 'some string', 'some_string', -1, 66666666666666666666666, 7.77, 0],
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

class TestPersonAutoLookupForm(TestPersonForm):
    form_class = PersonAutoLookupForm
    form_super_class = PersonForm

class TestCharacterPersonForm(TestPersonAutoLookupForm):
    form_class = CharacterPersonForm
    form_super_class = PersonAutoLookupForm

class TestActorNameAutoLookupForm(UniversalFormTest):
    form_class = ActorNameAutoLookupForm
    all_fields_are_required = True
    valid_data_dict = {'actor_name': 'test_name'}
