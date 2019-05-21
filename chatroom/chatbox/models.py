from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime
import time
from PIL import Image

# Model helper functions
def validate_size(f):
    filesize = f.size

    if filesize > 2097152:
        raise ValidationError("The maximum file size that can be uploaded is 2MB")
    else:
        return f

def autoresize_image(image_path):
    image = Image.open(image_path)
    width = image.size[0]
    
    if width > settings.IMAGE_MAX_WIDTH:
        height = image.size[1]
        reduce_factor = settings.IMAGE_MAX_WIDTH / float(width)
        reduced_width = int(width * reduce_factor)
        reduced_height = int(height * reduce_factor)
        image = image.resize((reduced_width, reduced_height), Image.ANTIALIAS)
        image.save(image_path)

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=48,default='')
    
    def __str__(self):
        return self.name

class Post(models.Model):

    # username = models.CharField(max_length=32,default='user')
    url = models.URLField(max_length=250)
    metaimage = models.URLField(max_length=500,blank=True,null=True)
    text = models.TextField(blank=True,max_length=50000)
    title = models.CharField(max_length=64, default='')

    user = models.ForeignKey(User,default=0,on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE)

    datetime = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title

class Message(models.Model):

    #username = models.CharField(max_length=32,default='user')
    message_text = models.CharField(max_length=1000)
    #room_name = models.CharField(max_length=200,default='lobby')

    user = models.ForeignKey(User,default=0,on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,default=0,on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    datetime = models.BigIntegerField(default=0)

    def __str__(self):
        return self.message_text

class Notification(models.Model):
    name = models.CharField(max_length=48,default='')
    actor = models.ForeignKey(User, default=1, on_delete=models.DO_NOTHING, related_name='notification_actor')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='notification_users')
    text = models.CharField(max_length=80, default='')
    datetime = models.BigIntegerField(default=0)

    def __str__(self):
        return '%s-%d' % (self.topic,self.post.id) if self.post else self.topic.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #notifications = models.ManyToManyField(Notification)
    profile_picture = models.ImageField(blank=True,null=True,validators=[validate_size])
    subscriptions = models.ManyToManyField(Topic)

    def __str__(self):
        return "%s's profile" % self.user.username

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        if self.profile_picture:
            autoresize_image(self.profile_picture.path)