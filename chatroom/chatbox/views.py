from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import Message

import json

# Create your views here.
def index(request):
    return render(request,'chat/index.html',{})

def room(request, room_name):
    messages = Message.objects.filter(room_name=room_name)

    return render(request,'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'chat_history' : messages,
    })