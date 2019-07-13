from django.test import SimpleTestCase
from django.urls import reverse, resolve
import random

class UniversalURLtest(SimpleTestCase):
    app_name = ''
    namespace = ''
    urlpatterns = []

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
                        print('converter class not found!!! for ', url_path, ' converter = ', converter)
                if args == []:
                    reverse_url = reverse(self.namespace + ':' + url_path.name)
                    resolved_url = resolve(reverse_url)
                    self.assertEqual(resolved_url.app_name, self.app_name)
                    self.assertEqual(resolved_url.namespace, self.namespace)
                    self.assertEqual(resolved_url.func, url_path.callback)
                    print('   !!!   checked url:   ', reverse_url)
                    checked_url_count = checked_url_count + 1
                else:
                    reverse_url = reverse(self.namespace + ':' + url_path.name, args=args)
                    resolved_url = resolve(reverse_url)
                    self.assertEqual(resolved_url.app_name, self.app_name)
                    self.assertEqual(resolved_url.namespace, self.namespace)
                    self.assertEqual(resolved_url.func, url_path.callback)
                    print('   !!!   checked url:   ', reverse_url, ' with args: ', args)
                    checked_url_count = checked_url_count + 1
            self.assertEqual(checked_url_count, len(self.urlpatterns))
            print('   !!!   All {} url_paths are checked   !!!   '.format(checked_url_count))
