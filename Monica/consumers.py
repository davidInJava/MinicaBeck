from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer, channel_layers
from asgiref.sync import async_to_sync, sync_to_async
import json
import datetime
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.messages import add_message
from django.db import connection
from profileUser.models import User
import jwt
from django.db.models import Q
from profileUser.models import Messages, Chat


class YourConsumer(AsyncConsumer):
    channel_layer = get_channel_layer()
    uid_chat = None
    array_chat = None

    @database_sync_to_async
    def get_messages(self, chat_uid, lim):
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM profileuser_messages WHERE uid_Chat_id = {chat_uid} ORDER BY date DESC LIMIT {lim}")
            rows = cursor.fetchall()

            return rows

    @database_sync_to_async
    def add_message(self, nickname, text, chat_uid):
        chat_uid = int(chat_uid)
        print(chat_uid, nickname, text)

        chat = Chat.objects.get(uid=chat_uid)
        print(chat)
        if chat:
            message = Messages.objects.new_message(chat_uid, nickname, text)
            message.save()
            return message

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    async def authenticate_user(self, token):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded['id']
            user = await self.get_user(user_id)
            return user
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    async def websocket_connect(self, event):
        query_string = self.scope['query_string'].decode('utf-8')
        params = {param.split('=')[0]: param.split('=')[1] for param in query_string.split('&')}

        token = params.get('token')
        chat_uid = params.get('chatuid')
        print(token)
        user1 = await self.authenticate_user(token)
        self.scope["user"] = user1
        self.uid_chat = chat_uid
        await self.channel_layer.group_add(f'chat_{self.uid_chat}', self.channel_name)
        await self.send({"type": "websocket.accept"})

        self.array_chat = await self.get_messages(chat_uid, 50)
        js = {}
        a = 0
        for i in self.array_chat:
            js[str(a)] = {
                'nickname': i[1],
                'time': i[2].isoformat(),
                'message': i[3],
            }
            a += 1

        await self.channel_layer.group_send(
            f'chat_{self.uid_chat}',  # Имя группы
            {  # Сообщение
                'type': 'chat_message',
                'chat_uid': self.uid_chat,
                'messages': js
            }
        )

    async def websocket_receive(self, text_data):

        uid = self.uid_chat
        nickname = json.loads(text_data["text"])['nickname']
        text = json.loads(text_data["text"])['message']

        a = await self.add_message(nickname, text, uid)
        self.array_chat = await self.get_messages(uid, 50)
        js = {}
        a = 0
        for i in self.array_chat:
            js[str(a)] = {
                'nickname': i[1],
                'time': i[2].isoformat(),
                'message': i[3],
            }
            a += 1

        await self.channel_layer.group_send(
            f'chat_{self.uid_chat}',  # Имя группы
            {  # Сообщение
                'type': 'chat_message',
                'chat_uid': self.uid_chat,
                'messages': js
            }
        )

    async def chat_message(self, event):
        print("Sending message:", event)
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event)  # Преобразуем словарь в JSON
        })

    async def websocket_disconnect(self, event):
        pass


