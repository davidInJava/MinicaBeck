from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer, channel_layers
from asgiref.sync import async_to_sync
import json
from channels.db import database_sync_to_async
from django.conf import settings
from profileUser.models import User
import jwt


class YourConsumer(AsyncConsumer):
    channel_layer = get_channel_layer()
    uid_chat = None

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
        await self.channel_layer.group_add( f'chat_{self.uid_chat}', self.channel_name)
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        print("111111111111111")
        # data = json.loads(text_data)
        print(json.loads(text_data['text'])['message'], self.uid_chat)

        await self.channel_layer.group_send(
            f'chat_{self.uid_chat}',  # Имя группы
            {  # Сообщение
                'type': 'chat_message',
                'chat_uid': self.uid_chat,
                'message': json.loads(text_data['text'])['message']
            }
        )

    async def chat_message(self, event):
        print("Sending message:", event)
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def websocket_disconnect(self, event):
        pass
