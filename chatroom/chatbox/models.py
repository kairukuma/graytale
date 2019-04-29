from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
import time

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=48,default='')
    
    def __str__(self):
        return self.name

class Post(models.Model):

    # username = models.CharField(max_length=32,default='user')
    url = models.URLField(max_length=250)
    text = models.TextField(blank=True,max_length=10000)
    title = models.CharField(max_length=64, default='')

    user = models.ForeignKey(User,default=0,on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE)

    datetime = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Message(models.Model):

    #username = models.CharField(max_length=32,default='user')
    message_text = models.CharField(max_length=1000)
    #room_name = models.CharField(max_length=200,default='lobby')

    user = models.ForeignKey(User,default=0,on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,default=0,on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    datetime = models.IntegerField(default=0)

    def __str__(self):
        return self.message_text

class Notification(models.Model):
    name = models.CharField(max_length=48,default='')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #notifications = models.ManyToManyField(Notification)
    subscriptions = models.ManyToManyField(Topic)