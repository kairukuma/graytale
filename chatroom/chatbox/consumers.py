from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, Notification, Topic, Post

from datetime import datetime
from webpush import send_group_notification, send_user_notification

import json
import time

def send_admin_notifications():
    payload = {"head": "Welcome!", "body": "Hello World"}

    for usr in User.objects.filter(groups__name='admin'):
        send_user_notification(user=usr, payload=payload, ttl=1000)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        post_id = self.scope['url_route']['kwargs']['post_id'] if 'post_id' in self.scope['url_route']['kwargs'] else None
        if post_id is not None and Post.objects.filter(id=post_id).exists():
            self.post = Post.objects.get(id=post_id)
        else:
            self.post = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            'notifications',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            'notifications',
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if len(self.user.username) == 0 or len(message.strip()) == 0:
            return

        dt = datetime.now()

        topic = Topic.objects.get(name=self.room_name)

        m = Message(
            message_text=message,
            user=self.user,
            topic=topic,
            post_id = self.post,
            datetime=time.mktime(dt.timetuple()),
        )
        m.save()

        if Notification.objects.filter(topic=topic, post=self.post).exists():
            n = Notification.objects.get(topic=topic, post=self.post)
        else:
            n = Notification.objects.create(name=topic.name,topic=topic,post=self.post)

        n.actor = self.user
        
        n.datetime = time.mktime(dt.timetuple())
        n.text = message
        n.users.set(User.objects.all())
        n.save()

        # send_admin_notifications()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'profile_pic': self.user.profile.profile_picture.url if self.user.profile.profile_picture else None,
                'username': self.user.username,
            }
        )

        await self.channel_layer.group_send(
            'notifications',
            {
                'type': 'notification',
                'room_name': self.room_name,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_pic = event['profile_pic']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'profile_pic': profile_pic,
        }))

    async def notification(self, event):
        room_name = event['room_name']

        await self.send(text_data=json.dumps({
            'type': 'notification',
            'room_name' : room_name,
        }))