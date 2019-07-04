from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from core.models import Theme
from img.forms import ImageForm

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
        context.update({'image_form': ImageForm()})
        questions = object.questions.all()
        if questions.exists() and user.is_authenticated:
            replied_questions = questions.filter(replies__user=user)
            created_questions = questions.filter(user=user)
            question_total_dict = {
                  'Всего вопросов': questions.count(),
                  'Отвечено Вами': replied_questions.count(),
                  'Добавлено Вами': created_questions.count(),
                  'Доступно Вам': questions.count() - replied_questions.count() - created_questions.count(),
            }
            context.update({'question_total_dict': question_total_dict})
        return context

class OrderingMultipleObjectMixin(MultipleObjectMixin):
    template_name='core/common_list.html'
    paginate_by = 10

    def get_card_type(self):
        card_type = self.request.GET.get('card_type')
        if not card_type:
            if self.model == Theme:
                return 'view_module'
            return 'view_list'
        return card_type

    def get_order(self):
        order = self.request.GET.get('order')
        if not order:
            return 'alphabet_incr'
        return order

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        model = self.model
        qs = model.validation.passed()
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

    def get_paginate_by(self, *args, **kwargs):
        paginate_by = self.request.GET.get('paginate_by')
        if not paginate_by:
            return self.paginate_by
        return int(paginate_by)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        paginate_by = self.get_paginate_by()
        order = self.get_order()
        order_dict = {
            "alphabet_incr": "По алфавиту (А-Я)",
            "alphabet_decr": "По алфавиту (Я-А)",
            "rate_incr": "По возрастанию рейтинга",
            "rate_decr": "По убыванию рейтинга",
            "validated_incr": "По возрастанию даты добавления",
            "validated_decr": "По убыванию даты добавления",
        }
        if self.model != Theme:
            order_dict.update({
                "year_incr": "По возрастанию даты создания (рождения)",
                "yaer_decr": "По убыванию даты создания (рождения)",
            })
        card_type = self.get_card_type()
        page_suffix = '&paginate_by={}&order={}&card_type={}'.format(paginate_by, order, card_type)
        card_path = 'core/cards/{}.html'.format(card_type)
        context.update({
            'paginate_by': paginate_by,
            'pagination_list': [10, 20, 30],
            'order': order,
            'order_dict': order_dict,
            'card_type': card_type,
            'card_list': ['view_list', 'view_module'],
            'card_path': card_path,
            'page_suffix': page_suffix,
        })
        return context

class ValidationMultipleObjectMixin(MultipleObjectMixin):
    template_name='core/validation_list.html'

    def get_queryset(self, *args, **kwargs):
        model = self.model
        user = self.request.user
        qs = model.validation.current(user)
        if user.is_staff:
            qs = qs.order_by('user_is_creator', '-proposed')
        qs = qs.order_by('already_voted', '-approve_score')
        return qs
