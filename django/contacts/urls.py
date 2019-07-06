from django.urls import path
from contacts.views import *

# comon_prefix: 'contacts/'
app_name = 'contacts'
urlpatterns = [
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/reply/', ReplyCreateView.as_view(), name='message_reply'),
    path('messages/<int:pk>/faq/', add_to_faq, name='add_to_faq'),
    path('messages/faq/', FAQListView.as_view(), name='faq'),
]
