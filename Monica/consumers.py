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

    async def authenticate_user(self, token):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded['id']
            user = await self.get_user(user_id)
            return user
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)
    print(channel_layers)
    async def websocket_connect(self, event):
        query_string = self.scope['query_string'].decode('utf-8')
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break

        user1 = await self.authenticate_user(token)
        self.scope["user"] = user1
        print(self.scope["user"])
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": text_data,
            }
        )

    async def chat_message(self, event):

        event = event["message"]['text']
        my_dict = json.loads(event)
        print(my_dict['message'])

        await self.send({
            "type": "websocket.send",
            "text": my_dict['message']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard("chat", self.channel_name)