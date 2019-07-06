from django import forms
from contacts.models import *

class UserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['category', 'title', 'text', 'is_private', 'user']
        widgets = {
            'user': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'rows': "3"})
        }
        help_texts = {'is_private': 'Сообщение, отмеченное как "личное" будет доступно только Вам и команде сайта'}

class AnonymousMessageForm(forms.ModelForm):
    class Meta:
        model = AnonymousMessage
        fields = ['name', 'email', 'category', 'title', 'text', 'is_private']
        widgets = {'text': forms.Textarea(attrs={'rows': "3"})}
        help_texts = {'is_private': 'Сообщение, отмеченное как "личное" будет доступно только Вам и команде сайта'}

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text', 'user', 'message']
        widgets = {
            'user': forms.HiddenInput(),
            'message': forms.HiddenInput(),
            'text': forms.Textarea(attrs={'rows': "3"}),
        }
