from asgiref.sync import async_to_sync
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import connection
from profileUser.models import User
import jwt
import json



#TODO нужно будет реализовать логику добавления чата в реальном времени
class ChatConsumer(AsyncConsumer):
    channel_layer = get_channel_layer()

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
    @database_sync_to_async
    def get_all_chats(self, nickname):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM profileuser_chat where user1_id = '{nickname}' or user2_id = '{nickname}'")
            a = cursor.fetchall()
            return list(a)

    async def get_chats(self, nickname):
        return await self.get_all_chats(nickname)

    @database_sync_to_async
    def get_last_message(self, chat_uid):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * from profileuser_messages where uid_Chat_id = '{chat_uid}' ORDER BY date DESC LIMIT 1")
            a = cursor.fetchall()
            return list(a)
    async def last_message(self, chat_uid):
        return await self.get_last_message(chat_uid)


    async def websocket_connect(self, event):
        query_string = self.scope['query_string'].decode('utf-8')
        params = {param.split('=')[0]: param.split('=')[1] for param in query_string.split('&')}

        token = params.get('token')
        user = await self.authenticate_user(token)

        d = await self.get_chats(user.nickname)
        c = {

        }
        ii = 0

        for i in d:
            chat_id = i[1]
            um_het = None
            if i[2] == user.nickname:
                um_het = i[3]
            else:
                um_het = i[2]
            nick_message = None
            last_message_text = None
            text = None
            lastmessage = await self.last_message(chat_id)
            if (lastmessage):
                if lastmessage[0][1] == user.nickname:
                    nick_message = 'Вы'
                else:
                    nick_message = lastmessage[0][1]
                text = lastmessage[0][3]
            c[ii] ={
                'chat_id': chat_id,
                'um_het': um_het,
                'nick_message': nick_message,
                'text': text,
            }
            ii+=1






        await self.send({"type": "websocket.accept"})
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(c)
        })
        print(c)

    async def websocket_disconnect(self, event):
        pass
