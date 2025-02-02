import uuid
from datetime import datetime, timedelta
from django.conf import settings

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.http import JsonResponse

from profileUser.managers import UserManager, ChatManager
import jwt





class User(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=20, null=False, unique=True)
    email = models.EmailField(unique=True, null=True)
    role = models.CharField(max_length=120, default='user')
    number_phone = models.CharField(max_length=20, unique=True, null=True)
    password = models.CharField(max_length=120, null=False)
    photo = models.CharField(max_length=255, null=False)
    _token = None


    objects = UserManager()
    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        if (self.email is not None):
            return self.nickname + ' ' + self.email
        else:
            return self.nickname

    def set_token(self, token):
        print("set_token", token)
        self._token = token
    @property
    def token(self):
        if (self._token is not None):
            print("В иф токена")
            return self._generate_auth_token(self._token)
        else:
            print("да это проблема токена")
            return self._generate_jwt_token()

    def _generate_auth_token(self, token):

        if 'exp' in token:
            del token['exp']
        dt = datetime.now() + timedelta(days=1)
        new_token = jwt.encode({
            'id': self.pk,
            'exp': dt.timestamp(),
            'nickname': self.nickname,
        }, settings.SECRET_KEY, algorithm='HS256')
        print("Generate auth")
        return new_token

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)
        try:
            token = jwt.encode({
                'id': self.pk,
                'exp': int(dt.timestamp()),  # Используем метод timestamp(),s
                'nickname': self.nickname,
            }, settings.SECRET_KEY, algorithm='HS256')
            return token
        except Exception as e:
            print(e)




class Chat(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    user1 = models.ForeignKey('User', on_delete=models.CASCADE, null=False, to_field='nickname',
                              related_name='chats_as_user1')
    user2 = models.ForeignKey('User', on_delete=models.CASCADE, null=False, to_field='nickname',
                              related_name='chats_as_user2')
    uid = models.AutoField(primary_key=True)
    objects = ChatManager()

    def __str__(self):
        return f'Chat between {self.user1.nickname} and {self.user2.nickname}'
class MessageChat(models.Manager):
    use_in_migrations = True

    def new_message(self, uid_chat, nickname, text):
        try:
            chat = Chat.objects.get(uid=uid_chat)
            if nickname in [chat.user1.nickname, chat.user2.nickname]:
                new_message = self.create(
                    uid_Chat=chat,
                    user_nickname=nickname,
                    text=text
                )
                return new_message
            return JsonResponse({'error': 'Вы не можете отправить сообщение в этот чат'}, status=400)
        except Chat.DoesNotExist:
            return JsonResponse({'error': 'Не найден такой чат'}, status=400)


class Messages(models.Model):
    uid_Chat = models.ForeignKey('Chat', on_delete=models.CASCADE, null=False, to_field='uid')
    user_nickname = models.CharField(max_length=255, null=False, unique=False)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    objects = MessageChat()


    def __str__(self):
        return self.text

