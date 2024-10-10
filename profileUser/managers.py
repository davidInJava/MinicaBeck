from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.http import JsonResponse

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, nickname, number_phone=None, password = None,  email = None, **extra_fields):
        """
        Создает и сохраняет пользователя с введенным им email и паролем.
        """
        if not nickname :
            raise ValueError('не указан email или password')
        if not number_phone and not email:
            raise ValueError('Не указан номер телефона')
        user = self.model(nickname=nickname, number_phone=number_phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, nickname, number_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(nickname, number_phone, password, **extra_fields)

    def create_superuser(self, nickname, number_phone, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(nickname, number_phone, password, **extra_fields)

class ChatManager(models.Manager):
    use_in_migrations = True

    def create_chat(self, user1_nickname, user2_nickname, name):
        if user1_nickname == user2_nickname:
            raise ValueError("Вы не можете написать самому себе")

        user = get_user_model()
        try:
            user1 = user.objects.get(nickname=user1_nickname)
            user2 = user.objects.get(nickname=user2_nickname)

            existing_chat = self.filter(
                user1__nickname=user1_nickname,
                user2__nickname=user2_nickname
            ).first()
            existing_chat1 = self.filter(
                user1__nickname=user2_nickname,
                user2__nickname=user1_nickname
            ).first()
            if existing_chat or existing_chat1:
                print(existing_chat1)
                if existing_chat:
                    return existing_chat
                else:
                    return existing_chat1

            new_chat = self.create(
                name=name,
                user1=user1,
                user2=user2
            )

            return new_chat

        except user.DoesNotExist:
            return JsonResponse({'error': 'Пользователь не найден'}, status=400)



