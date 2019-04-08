from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic

from datetime import datetime

from .models import Message, Post, Topic

import json, time

# Create your views here.

""" Views Classes """

class Register(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'registration/register.html'

class Create(forms.Form):
    title = forms.CharField(label='Title')
    topic = forms.CharField(label='Topic')
    url = forms.URLField(label='URL')
    text = forms.CharField(label='Body')

""" Views Functions """

def index(request):
    return render(request,'chat/index.html',{})

def room(request, room_name='graytale'):
    topic = Topic.objects.filter(name=room_name)

    if len(topic) == 0:
        raise Http404("Page does not exist")

    messages = reversed(Message.objects.filter(room_name=room_name, post_id=0).order_by('-datetime')[:20])

    if room_name == 'graytale':
        posts = Post.objects.order_by('datetime')[:10]
    else:
        posts = Post.objects.filter(topic=room_name).order_by('datetime')[:10]

    return render(request,'chat/room.html', {
        'room_name': mark_safe(room_name),
        'room_name_json': mark_safe(json.dumps(room_name)),
        'chat_history' : messages,
        'posts': posts,
    })

def post_view(request, room_name='graytale', post_id='0'):
    post = Post.objects.filter(topic=room_name,id=post_id)[0]
    messages = reversed(Message.objects.filter(room_name=room_name, post_id=post_id).order_by('-datetime')[:20])

    return render(request,'chat/post.html', {
        'chat_history': messages,
        'room_name': room_name,
        'room_name_json': mark_safe(json.dumps(room_name)),
        'id': post_id,
        'post': post,
    })

def user(request, user_name):
    u = User.objects.get(username=user_name)
    messages = Message.objects.filter(username=user_name).order_by('datetime')
    posts = Post.objects.filter(username=user_name).order_by('datetime')
    
    return render(request,'chat/user.html', {
        'user' : u,
        'messages' : messages,
        'posts' : posts,
        'room_name' : 'Topic',
    })

def create(request):

    if request.user.id is None:
        return

    if request.method == 'POST':
        form = Create(request.POST)

        if form.is_valid():

            dt = datetime.now()

            p = Post(
                url = request.POST['url'],
                text = request.POST['text'],
                title = request.POST['title'],
                topic = request.POST['topic'],
                datetime = time.mktime(dt.timetuple()),
                username = request.user,
            )
            p.save()

            return HttpResponseRedirect(reverse_lazy('index'))
    else:
        form = Create()
    return render(request, 'create.html', {'form': form})