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

class Register(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'registration/register.html'

class Create(forms.Form):
    title = forms.CharField(label='Title')
    topic = forms.CharField(label='Topic')
    # url = forms.URLField(label='URL')
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

        if Notification.objects.filter(topic=topic).exists():
            notification = Notification.objects.get(topic=topic)
            if request.user in notification.users.all():
                notified = True

        topics[topic.name] = {
            'topic': topic.name,
            'notification': notified,
        }

    return topics

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
    notification = None

    currentTopic = Topic.objects.get(name=room_name)
    if Notification.objects.filter(topic=currentTopic).exists():
        notification = Notification.objects.get(topic=currentTopic)
        if request.user in notification.users.all():
            notification.users.remove(request.user)
            notification.save()

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

    # If request method get
    return render(request,'chat/room.html', {
        'room_name': mark_safe(room_name),
        'room_name_json': mark_safe(json.dumps(room_name)),
        'chat_history' : messages,
        'subscribed' : subscribed,
        'subscriptions' : subscriptions,
        'subscribable': True,
        'topics' : get_topics(request),
        'posts': posts,
    })

def post_view(request, room_name='graytale', post_id='0'):

    topic = Topic.objects.get(name=room_name)
    post = Post.objects.filter(topic=topic,id=post_id)[0]
    subscriptions, topic, messages = room_data(request, room_name, post)

    if topic is None:
        raise Http404("Page does not exist")

    subscribed = False if len(subscriptions) == 0 else len(subscriptions.filter(name=room_name)) > 0

    return render(request,'chat/post.html', {
        'chat_history': messages,
        'room_name': room_name,
        'room_name_json': mark_safe(json.dumps(room_name)),
        'subscribed' : subscribed,
        'subscriptions': subscriptions,
        'subscribable': True,
        'id': post_id,
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

def create(request):

    if request.user.id is None:
        return

    if request.method == 'POST':
        form = Create(request.POST)
        print(form.is_valid())

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
                datetime = time.mktime(dt.timetuple()),
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