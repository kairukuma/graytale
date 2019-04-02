from asgiref.sync import async_to_sync
from channels.auth import get_user
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from .models import Message

from datetime import datetime
import json

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

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

        if len(self.user.username) == 0:
            return

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        dt = datetime.now()

        m = Message(
            message_text=message,
            room_name=self.room_name,
            username=self.user.username,
            year=dt.year,month=dt.month,day=dt.day,hour=dt.hour,minute=dt.minute,second=dt.second
        )
        m.save()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))