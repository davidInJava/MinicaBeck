import uuid
from datetime import datetime, timedelta
from django.conf import settings

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
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

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.timestamp(),  # Используем метод timestamp(),s
            'nickname': self.nickname,
        }, settings.SECRET_KEY, algorithm='HS256')

        return token


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
