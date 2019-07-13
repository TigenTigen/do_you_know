from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from termcolor import colored
import random

class UniversalURLtest(SimpleTestCase):
    app_name = ''
    namespace = ''
    urlpatterns = []

    def setUp(self):
        print(colored('Testing URLS!!!', 'yellow'))

    def green(self, message):
        print(colored(message, 'green'))

    def red(self, message):
        print(colored(message, 'red'))

    def test_resolve_url(self):
        if self.app_name != '' and self.urlpatterns != []:
            print('...')
            random.shuffle(self.urlpatterns)
            checked_url_count = 0
            for url_path in self.urlpatterns:
                args = []
                for converter in url_path.pattern.converters.values():
                    from django.urls import converters
                    if isinstance(converter, converters.IntConverter):
                        args.append(random.randint(1, 1000))
                    elif isinstance(converter, converters.StringConverter):
                        args.append('some_string')
                    elif isinstance(converter, converters.UUIDConverter):
                        args.append('some_uuid')
                    elif isinstance(converter, converters.SlugConverter):
                        args.append('some_slug')
                    elif isinstance(converter, converters.PathConverter):
                        args.append('some_path')
                    else:
                        self.red('!!!   converter class not found for {}, converter = {}'.format(url_path, converter))
                if args == []:
                    reverse_url = reverse(self.namespace + ':' + url_path.name)
                    resolved_url = resolve(reverse_url)
                    self.assertEqual(resolved_url.app_name, self.app_name)
                    self.assertEqual(resolved_url.namespace, self.namespace)
                    self.assertEqual(resolved_url.func, url_path.callback)
                    self.green('   OK   checked url:   {}'.format(reverse_url))
                    checked_url_count = checked_url_count + 1
                else:
                    reverse_url = reverse(self.namespace + ':' + url_path.name, args=args)
                    resolved_url = resolve(reverse_url)
                    self.assertEqual(resolved_url.app_name, self.app_name)
                    self.assertEqual(resolved_url.namespace, self.namespace)
                    self.assertEqual(resolved_url.func, url_path.callback)
                    self.green('   OK   checked url:   {}   with args {}'.format(reverse_url, args))
                    checked_url_count = checked_url_count + 1
            self.assertEqual(checked_url_count, len(self.urlpatterns))
            self.green('   !!!   All {} url_paths are checked   !!!   '.format(checked_url_count))

class UniversalFormTest(TestCase):
    form_class = None
    form_super_class = None
    form_model_class = None
    all_fields_are_required = False
    valid_data_dict = {}
    field_validation_check_dict = {}

    @classmethod
    def setUpTestData(cls):
        if cls.form_class:
            print(colored('Testing form: {}'.format(cls.form_class), 'yellow'))
            cls.field_validation_check_dict = cls.get_field_validation_check_dict(cls)

    def setUp(self):
        if self.form_class:
            self.form = self.form_class()
            self.valid_data_dict = self.get_valid_data_dict()

    def get_valid_data_dict(self):
        return self.get_valid_data_dict

    def get_field_validation_check_dict(self):
        return self.field_validation_check_dict

    def green(self, message):
        print(colored(message, 'green'))

    def red(self, message):
        print(colored(message, 'red'))

    def cyan(self, message):
        print(colored(message, 'cyan'))

    def print_invalid_form_errors(self, form):
        if form.non_field_errors():
            print('   !!! form is invalid:  ', form.non_field_errors())
        for field in form:
            if field.errors:
                print('   !!! invalid field value: ', field.name, field.errors)

    def test_form_class(self):
        if self.form_super_class:
            self.assertIsInstance(self.form, self.form_super_class)
        if self.form_model_class:
            self.assertEqual(self.form.Meta.model, self.form_model_class)

    def test_fields(self):
        if self.form_class:
            print('...')
            generated_fields = self.form.fields
            required_fields = self.form_class.Meta.fields
            checked_fields = 0
            for field in required_fields:
                self.assertIn(field, generated_fields)
                checked_fields = checked_fields + 1
                self.green('   OK   field {} in generated_fields'.format(field))
            self.assertEqual(checked_fields, len(required_fields))
            self.green('   !!!   All {} required_fields are generated   !!!   '.format(checked_fields))

    def test_required_fields(self):
        if self.all_fields_are_required:
            print('...')
            for field in self.form.fields.values():
                self.assertTrue(field.required)
            self.green('   !!!   All fields are required   !!!   ')

    def test_form_validation(self):
        if self.form_class:
            print('...')
            data_dict = self.valid_data_dict
            form = self.form_class(data_dict)
            if form.is_valid():
                self.assertTrue(form.is_valid())
                self.green('   OK   Form passed through base validation with valid_data_dict: {}'.format(data_dict))
            else:
                self.print_invalid_form_errors(form)

    def test_field_validation(self):
        if self.form_class and self.field_validation_check_dict != {}:
            print ('...')
            for field_name, wrong_choices in self.field_validation_check_dict.items():
                print('   ----------   Checking validation for field:   ', field_name)
                data_dict = self.get_valid_data_dict()
                for choice in wrong_choices:
                    data_dict.update({field_name: choice})
                    form = self.form_class(data_dict)
                    if form.is_valid():
                        self.cyan('   !!!   Invalid value has broken through: {}'.format(choice))
                    else:
                        try:
                            self.assertFalse(form.is_valid())
                            try:
                                self.assertNotIn(field_name, form.cleaned_data)
                            except:
                                self.assertNotEqual(form.cleaned_data[field_name], choice)
                            self.assertIsNotNone(form[field_name].errors)
                            self.green('   OK   Invalid value has been cought: {}'.format(choice))
                        except:
                            self.red('   !!!   Test failed   !!! Check form validation: ')
                            self.print_invalid_form_errors(form)

    def test_save_method_with_no_commit(self):
        if self.form_class:
            data_dict = self.valid_data_dict
            form = self.form_class(data_dict)
            if form.is_valid():
                new_object = form.save(commit = False)
                self.assertIsNone(new_object.id)

    def test_save_method(self):
        if self.form_class:
            data_dict = self.valid_data_dict
            form = self.form_class(data_dict)
            if form.is_valid():
                new_object = form.save()
                self.assertIsNotNone(new_object.id)
