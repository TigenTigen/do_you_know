from django.contrib import admin
from contacts.models import *

admin.site.register(Category)
admin.site.register(Message)
admin.site.register(UserMessage)
admin.site.register(AnonymousMessage)
admin.site.register(Reply)
