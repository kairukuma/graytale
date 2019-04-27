from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, Notification, Topic

from datetime import datetime

import json
import time

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.post_id = self.scope['url_route']['kwargs']['post_id'] if 'post_id' in self.scope['url_route']['kwargs'] else 0

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

        m = Message(
            message_text=message,
            user=self.user,
            room_name=self.room_name,
            username=self.user.username,
            post_id = self.post_id,
            datetime=time.mktime(dt.timetuple()),
        )
        m.save()

        topic = Topic.objects.get(name=self.room_name)

        if Notification.objects.filter(topic=topic).exists():
            n = Notification.objects.get(topic=topic)
        else:
            n = Notification.objects.create(name=topic.name,topic=topic)

        n.users.set(User.objects.all())
        n.save()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
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

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
        }))

    async def notification(self, event):
        room_name = event['room_name']

        await self.send(text_data=json.dumps({
            'type': 'notification',
            'room_name' : room_name,
        }))

"""class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        #self.room_name = self.scope['url_route']['kwargs']['room_name']
        #self.room_group_name = 'chat_%s' % self.room_name
        self.post_id = self.scope['url_route']['kwargs']['post_id'] if 'post_id' in self.scope['url_route']['kwargs'] else 0

        # Join room group
        await self.channel_layer.group_add(
            'notifications',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
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

        print('notification trigger')

        # Send message to room group
        await self.channel_layer.group_send(
            'notifications',
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print('notification')
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))"""