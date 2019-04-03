from asgiref.sync import async_to_sync
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from .models import Message

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

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
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
            room_name=self.room_name,
            username=self.user.username,
            post_id = self.post_id,
            datetime=time.mktime(dt.timetuple()),
        )
        m.save()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))