from django.contrib import admin

from .models import Message, Post, Topic
# Register your models here.
admin.site.register(Message)
admin.site.register(Post)
admin.site.register(Topic)