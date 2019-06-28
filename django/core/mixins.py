from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404

class ValidationSingleObjectMixin(SingleObjectMixin):
    def get_queryset(self, *args, **kwargs):
        model = self.model
        pk = self.kwargs.get('pk')
        object = get_object_or_404(model, pk=pk)
        if not object.is_validated():
            user = self.request.user
            qs = model.objects.all_with_perfetch_and_validation(pk, user)
        else:
            qs = model.objects.all_with_perfetch()
        return qs

class ValidationMultipleObjectMixin(MultipleObjectMixin):
    template_name='core/validation_list.html'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        model = self.model
        user = self.request.user
        return model.validation.current(user)
