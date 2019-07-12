from user.models import AdvUser
import factory

class AdvUserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user {}'.format(n))
    password = 'unittest'
    email = factory.Sequence(lambda n: 'email_for_user_{}@factory.com'.format(n))

    class Meta:
        model = AdvUser

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
