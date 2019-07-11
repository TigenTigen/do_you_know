from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from contacts.forms import *
from contacts.models import Message

class MessageCreateView(CreateView):
    template_name = 'contacts/message_create_form.html'

    def get_form_class(self):
        user = self.request.user
        if user.is_authenticated:
            return UserMessageForm
        return AnonymousMessageForm

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial.update({'user': user.id})
        return initial

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            return reverse_lazy('user:profile')
        return reverse_lazy('contacts:message_list')

class MessageListView(ListView):
    model = Message

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.exclude(is_private=True)
        return qs

class ReplyCreateView(CreateView):
    form_class = ReplyForm
    success_url = reverse_lazy('contacts:message_list')
    template_name = 'contacts/reply_create_form.html'

    def get_initial(self):
        initial = super().get_initial()
        message_pk = self.kwargs['pk']
        initial.update({'user': self.request.user.id, 'message': message_pk})
        return initial

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        message_pk = self.kwargs['pk']
        message = get_object_or_404(Message, pk=message_pk)
        context.update({'message': message})
        return context

class FAQListView(ListView):
    queryset = Message.objects.filter(show_as_faq=True)
    template_name = 'contacts/faq.html'

def add_to_faq(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.replies.exists():
        message.show_as_faq = True
        message.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
