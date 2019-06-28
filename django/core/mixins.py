from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404

class ExtraContextSingleObjectMixin(SingleObjectMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        object = self.object
        if user.is_authenticated:
            user_is_creator = (user.id == object.created_by_user_id)
            if user_is_creator:
                context.update({'user_is_creator': True})
            else:
                if not object.is_validated() and user in object.user_voted.all():
                        context.update({'already_voted': True})
                user_rating = object.ratings.filter(user_rated=user)
                if user_rating.exists():
                    context.update({'current_user_rating': user_rating.get().value})
        return context

class ValidationMultipleObjectMixin(MultipleObjectMixin):
    template_name='core/validation_list.html'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        model = self.model
        user = self.request.user
        return model.validation.current(user)
