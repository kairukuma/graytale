from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

# Create your models here.
class Message(models.Model):

    dt = datetime.now()

    #user = models.ForeignKey(User,default=1,on_delete=models.CASCADE)
    username = models.CharField(max_length=32,default='user')
    message_text = models.CharField(max_length=1000)
    room_name = models.CharField(max_length=200,default='lobby')

    year = models.IntegerField(default=dt.year)
    month = models.IntegerField(default=dt.month)
    day = models.IntegerField(default=dt.day)
    hour = models.IntegerField(default=dt.hour)
    minute = models.IntegerField(default=dt.minute)
    second = models.IntegerField(default=dt.second)

    def __str__(self):
        return self.message_text

class Post(models.Model):

    username = models.CharField(max_length=32,default='user')
    url = models.URLField(max_length=250)