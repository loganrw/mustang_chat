import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth.models import User
import datetime


class TextRoomConsumer(AsyncWebsocketConsumer):

    # Save the messages to the database
    @database_sync_to_async
    def create_chat(self, sender, message):
        try:
            user = User.objects.get(first_name=sender)
        except User.DoesNotExist:
            obj = User(first_name=sender, last_name='')
            obj.save()
            new_message = Message.objects.create(user=obj, message=message, timestamp=datetime.datetime.now())

        if user:
            new_message = Message.objects.create(user=user, message=message, timestamp=datetime.datetime.now())

        new_message.save()
        return new_message

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        sender = text_data_json['sender']
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'text': message,
            'sender': sender
        })

    async def chat_message(self, event):
        # Receive message from room group
        message = event['text']
        sender = event['sender']
        new_message = await self.create_chat(sender, message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'text': new_message.message,
            'sender': new_message.user.first_name,
        }))
