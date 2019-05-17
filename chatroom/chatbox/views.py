from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from django.views import generic
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Message, Post, Topic, Profile, Notification

from datetime import datetime

from webpush import send_group_notification,send_user_notification

import json, time
import metadata_parser as mdp
import numpy as np

# Create your views here.

""" Views Classes """

class ImageUploadForm(forms.Form):
    image = forms.ImageField()

class GrayTaleUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user

class Register(generic.CreateView):
    form_class = GrayTaleUserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'registration/register.html'

class Create(forms.Form):
    title = forms.CharField(label='Title')
    topic = forms.CharField(label='Topic')
    text = forms.CharField(label='Body')

class Edit(forms.Form):
    title = forms.CharField(label='Title')
    text = forms.CharField(label='Body')

""" Assist Functions """

def room_data(request, room_name, post_id):

    if request.user.is_authenticated:
        try:
            subscriptions = request.user.profile.subscriptions.all()
        except:
            Profile.objects.create(user=request.user)
            subscriptions = request.user.profile.subscriptions.all()
    else:
        subscriptions = []
        
    if Topic.objects.filter(name=room_name).exists():
        topic = Topic.objects.get(name=room_name)
    else:
        return subscriptions, None, None

    messages = reversed(Message.objects.filter(topic=topic, post_id=post_id).order_by('-datetime')[:25])

    return subscriptions, topic, messages

def get_topics(request):
    topics = {}

    for topic in Topic.objects.all():
        notified = False

        if request.user.is_authenticated and Notification.objects.filter(topic=topic,users__in=[request.user]).exists():
            notified = True

        topics[topic.name] = {
            'topic': topic.name,
            'notification': notified,
        }

    return topics

def clear_notification(request, room_name, post_id):

    if not request.user.is_authenticated:
        return 

    notification = None

    currentTopic = Topic.objects.get(name=room_name)
    
    if Notification.objects.filter(topic=currentTopic,post=post_id,users__in=[request.user]).exists():
    
        notification = Notification.objects.get(topic=currentTopic,post=post_id,users__in=[request.user])
        notification.users.remove(request.user)
        notification.save()

""" Views Functions """

def index(request):
    return render(request,'chat/index.html',{})

@ensure_csrf_cookie
def room(request, room_name='graytale'):
    
    subscriptions, topic, messages = room_data(request, room_name, None)

    if topic is None:
        raise Http404("Page does not exist")

    if room_name == 'graytale':
        posts = Post.objects.order_by('-datetime')[:10]
    else:
        posts = Post.objects.filter(topic=topic).order_by('-datetime')[:10]

    # Check if user is subbed
    subscribed = False if len(subscriptions) == 0 else len(subscriptions.filter(name=room_name)) > 0

    # If user is on a page, remove its notification for the user
    clear_notification(request, room_name, None)

    # If request method post
    if request.method == 'POST':
        if request.POST['function'] == 'subscribe':
            # toggle subscription
            if subscribed:
                request.user.profile.subscriptions.remove(subscriptions.get(name=room_name))
            else:
                request.user.profile.subscriptions.add(Topic.objects.get(name=room_name))

            return HttpResponse(json.dumps({'subscribed': not subscribed}),
                       content_type="application/json")
        else:
            return False

    post_notifications = []


    for post in posts:
        if request.user.is_authenticated:
            if room_name == 'graytale':
                post_notification = Notification.objects.filter(post=post,users__in=[request.user]).exists()
            else: 
                post_notification = Notification.objects.filter(topic=topic,post=post,users__in=[request.user]).exists()
    
            post_notifications.append(post_notification)
        else:
            post_notifications.append(False)

    print(post_notifications)

    # If request method get
    return render(request,'chat/room.html', {
        'room_name': mark_safe(room_name),
        'room_name_json': mark_safe(json.dumps(room_name)),
        'chat_history' : messages,
        'subscribed' : subscribed,
        'subscriptions' : subscriptions,
        'subscribable': True,
        'topics' : get_topics(request),
        'posts': zip(post_notifications, posts),
    })

def post_view(request, room_name='graytale', post_id='0'):

    topic = Topic.objects.get(name=room_name)
    post = Post.objects.filter(topic=topic,id=post_id)[0]
    subscriptions, topic, messages = room_data(request, room_name, post)

    if topic is None:
        raise Http404("Page does not exist")

    subscribed = False if len(subscriptions) == 0 else len(subscriptions.filter(name=room_name)) > 0
    clear_notification(request, room_name, int(post_id))

    return render(request,'chat/post.html', {
        'chat_history': messages,
        'room_name': room_name,
        'room_name_json': mark_safe(json.dumps(room_name)),
        'subscribed' : subscribed,
        'subscriptions': subscriptions,
        'subscribable': True,
        'post_id': post_id,
        'topics': get_topics(request),
        'post': post,
    })

def user(request, user_name, msg_page=1, post_page=1):
    mpg = int(msg_page)
    ppg = int(post_page)

    u = User.objects.get(username=user_name)
    messages = Message.objects.filter(user=u).order_by('-datetime')
    posts = Post.objects.filter(user=u).order_by('-datetime')
    
    num_msg_pages = np.ceil(messages.count() / 20).astype(int)
    num_pst_pages = np.ceil(posts.count() / 20).astype(int)

    message_range = np.zeros((8,),dtype=int)
    message_indices = np.arange(num_msg_pages)[:8]
    message_range[message_indices] = message_indices + 1 # NEED TO IMPLEMENT PAGINATION FOR > 160 messages

    post_range = np.zeros((8,),dtype=int)
    post_indices = np.arange(np.ceil(posts.count() / 20).astype(int))[:8]
    post_range[post_indices] = post_indices + 1 # NEED TO IMPLEMENT PAGINATION FOR > 160 messages

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid() and request.user == u:
            image = form.cleaned_data['image']
            u.profile.profile_picture.save(image.name,form.cleaned_data['image'])
            u.save()

    return render(request,'chat/user.html', {
        'user' : request.user,
        'profile': u,
        'messages' : messages[(mpg-1)*20:mpg*20],
        'posts' : posts[(ppg-1)*20:ppg*20],
        'message_page': mpg,
        'post_page': ppg,
        'topics' : get_topics(request),
        'room_name' : 'Topic',
        'subscribable': False,
        'message_range': message_range,
        'post_range': post_range,
        'num_msg_pages': num_msg_pages,
        'num_pst_pages': num_pst_pages,
    })

def edit_post_view(request, room_name, post_id):

    post = Post.objects.get(id=post_id)

    if request.user != post.user and not request.user.groups.filter(name__in=['admin']).exists():
        raise Http404("Permission not granted to edit post.")
        

    if request.method == 'POST':
        form = Edit(request.POST)
        print(form,request.POST)
        if form.is_valid():
            url = request.POST['url']
            try:
                metadata = mdp.MetadataParser(url=url,search_head_only=True)
                metaimage = metadata.get_metadata_link('image')
            except:
                metaimage = None
        
            post.url = url
            post.text = request.POST['text']
            post.title = request.POST['title']
            post.metaimage = metaimage

            post.save()
            return HttpResponseRedirect(reverse_lazy('index'))
    
    form = Create()

    return render(request,'edit.html', {
        'form': form,
        'post': post,
        'topics': get_topics(request),
    })

def delete_post_view(request,room_name,post_id):
    
    post = Post.objects.get(id=post_id)

    if request.user != post.user and not request.user.groups.filter(name__in=['admin']).exists():
        raise Http404("Permission not granted to delete post.")

    if request.method == 'POST':
        if 'yes_button' in request.POST:
            post.delete()
            return HttpResponseRedirect(reverse_lazy('index'))
        else:
            return HttpResponseRedirect(reverse_lazy('index'))

    return render(request,'delete.html', {
        'post': post,
        'redirect_url': reverse_lazy('index'),
        'topics': get_topics(request),
    })

def create(request):

    if request.user.id is None:
        return

    if request.method == 'POST':
        form = Create(request.POST)

        if form.is_valid():

            dt = datetime.now()
            url = request.POST['url']
            try:
                metadata = mdp.MetadataParser(url=url,search_head_only=True)
                metaimage = metadata.get_metadata_link('image')
            except:
                metaimage = None
        
            p = Post(
                url = url,
                text = request.POST['text'],
                title = request.POST['title'],
                metaimage = metaimage,
                topic = Topic.objects.get(name=request.POST['topic']),
                datetime = int(time.mktime(dt.timetuple()) * 1e3 + dt._microsecond // 1e3),
                user = request.user,
            )

            p.save()

            # sendpush_post(request)

            return HttpResponseRedirect(reverse_lazy('index'))
    else:
        form = Create()

    return render(request, 'create.html', {
        'form': form,
        'topics': get_topics(request),
    })

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('index'))
    else:
        return login(request)

def notifications(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            topic_name = request.POST['topic']
            if 'post_id' in request.POST:
                post_id = request.POST['post_id']
                notification = Notification.objects.filter(topic=Topic.objects.get(name=topic_name),post=Post.objects.get(id=post_id),users__in=[request.user])
            else:
                notification = Notification.objects.filter(topic=Topic.objects.get(name=topic_name),post=None,users__in=[request.user])

            if not notification.exists():
                return JsonResponse(status=200,data={'notifications': []})

            notification = notification[0]
            notification.users.remove(request.user)

        user_notifications = Notification.objects.filter(users__in=[request.user])
        notification_data = []

        for n in user_notifications:
            data = {
                'actor' : n.actor.id,
                'datetime' : n.datetime,
                'text' : n.text,
                'topic' : n.topic.name,
            }

            if n.post is not None:
                data['post'] = n.post.id
            
            notification_data.append(data)
        
        return JsonResponse(status=200,data={
            "notifications": notification_data,
        })
    else:
        raise Http404("User must be logged in!")

@require_POST
@csrf_exempt
def sendpush(request):
    topic = Topic.objects.get(name=request.POST['room_name'])
    messages = Message.objects.filter(topic=topic).order_by('-datetime')

    if len(messages) > 1:
        last_message_time = messages[1].datetime
    else:
        last_message_time = 0

    if time.mktime(datetime.now().timetuple()) - last_message_time < 300:
        return JsonResponse(status=200, data={"message": "Web push too soon"})

    payload = {'head': 'Graytale Chatroom', 'body': 'New message from %s!' % topic}

    for u in User.objects.filter(groups__name='admin'):
        send_user_notification(user=u, payload=payload, ttl=1000)
    
    return JsonResponse(status=200, data={"message": "Web push successful"})

@require_POST
@csrf_exempt
def sendpush_post(request):
    payload = {'head': 'Graytale Post', 'body': 'New post created in %s!' % request.POST['topic']}
    send_user_notification(user=request.user, payload=payload, ttl=1000)