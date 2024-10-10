from django.contrib.auth.base_user import BaseUserManager


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