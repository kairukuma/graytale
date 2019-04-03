from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic

from datetime import datetime

from .models import Message, Post

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
    messages = Message.objects.filter(room_name=room_name).order_by('datetime')[:20]
    posts = Post.objects.order_by('datetime')[:10]

    return render(request,'chat/room.html', {
        'room_name': mark_safe(room_name),
        'room_name_json': mark_safe(json.dumps(room_name)),
        'chat_history' : messages,
        'posts': posts,
    })

def create(request):
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