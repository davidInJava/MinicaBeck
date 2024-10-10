from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json

from django.views.decorators.csrf import csrf_exempt
import jwt

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def register(request):
    if request.method == 'POST':
        obj = request.body.decode('utf-8')
        obj = json.loads(obj)
        nickname = obj["nickname"]
        phone = obj["number_phone"]
        password = obj["password"]

        User = get_user_model()
        try:
            new_user = User.objects.create_user(nickname=nickname, number_phone=phone, role='user', password=password)
            new_user.save()

            d = User.objects.get(nickname=nickname)
            return JsonResponse({'token': d.token}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def get_user(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_AUTHORIZATION')  # Извлечение токена из заголовка
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]  # Убираем 'Bearer ' из токена
            try:
                # Декодируем токен и получаем полезную нагрузку
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                user_id = decoded['id']  # Извлекаем идентификатор пользователя

                # Получаем пользователя из базы данных
                User = get_user_model()
                user = User.objects.get(pk=user_id)

                # Возвращаем данные о пользователе
                return JsonResponse({
                    'nickname': user.nickname,
                    'email': user.email,
                    'role': user.role
                })
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User does not exist.'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Authorization header missing or malformed.'}, status=400)

    return HttpResponse("Method not allowed", status=405)