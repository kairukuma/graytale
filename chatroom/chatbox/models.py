from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
import time

# Create your models here.
class Message(models.Model):

    dt = datetime.now()

    #user = models.ForeignKey(User,default=1,on_delete=models.CASCADE)
    username = models.CharField(max_length=32,default='user')
    message_text = models.CharField(max_length=1000)
    room_name = models.CharField(max_length=200,default='lobby')
    post_id = models.IntegerField(default=0)

    datetime = models.IntegerField(default=time.mktime(dt.timetuple()))

    def __str__(self):
        return self.message_text

class Post(models.Model):

    dt = datetime.now()

    username = models.CharField(max_length=32,default='user')
    topic = models.CharField(max_length=32, default='graytale')
    url = models.URLField(max_length=250)
    text = models.TextField(blank=True,max_length=10000)
    title = models.CharField(max_length=64, default='')

    datetime = models.IntegerField(default=time.mktime(dt.timetuple()))

    def __str__(self):
        return self.title

class Topic(models.Model):
    name = models.CharField(max_length=48,default='')
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField(Topic)