from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json

from django.views.decorators.csrf import csrf_exempt
import jwt
from django.db import connection
from .models import Chat, User

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def register(request):
    if request.method == 'POST':
        obj = request.body.decode('utf-8')
        obj = json.loads(obj)
        print(obj)
        nickname = obj["nickname"]
        if "number_phone" in obj.keys():
            phone = obj["number_phone"]
        else:
            phone = None
        if "email" in obj.keys():
            email = obj["email"]
        else:
            email = None
        if "number_phone" not in obj.keys() and "email" not in obj.keys():
            raise ValueError("Хотя бы одно из полей email или телефон должно быть заполнено")
        role = obj["role"]
        password = obj["password"]
        User = get_user_model()
        try:
            new_user = User.objects.create_user(nickname=nickname, number_phone=phone, email=email, role='user', password=password)
            new_user.save()

            d = User.objects.get(nickname=nickname)


            return JsonResponse({'token': d.token}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponse("Method not allowed", status=405)

@csrf_exempt
def authorisation(request):
    if request.method == 'POST':
        print(1111111)
        obj = request.body.decode('utf-8')
        obj = json.loads(obj)
        nickname = obj["nickname"]
        print(1111111)
        password = obj["password"]
        User = get_user_model()
        try:
            user = User.objects.get(nickname=nickname)
            print(user)
            if check_password(password, user.password):
                return JsonResponse({'token': user.token}, status=201)
            else:
                return JsonResponse({"error": "Неверный логин или пароль"}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"error": "Неверный логин или пароль"}, status=401)


@csrf_exempt
def get_user(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_AUTHORIZATION')  # Извлечение токена из заголовка
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]  # Убираем 'Bearer ' из токена
            try:

                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                user_id = decoded['id']  # Извлекаем идентификатор пользователя

                # Получаем пользователя из базы данных
                User = get_user_model()
                user = User.objects.get(pk=user_id)

                # Возвращаем данные о пользователе
                return JsonResponse({
                    'nickname': user.nickname,
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


@csrf_exempt
def find_user(request):
    if request.method == 'POST':
        obj = request.body.decode('utf-8')
        obj = json.loads(obj)
        nickname = obj["nickname"]
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT (nickname) FROM profileuser_user WHERE nickname LIKE '%{nickname}%' LIMIT 5")
            rows = cursor.fetchall()
            return JsonResponse({'users': rows}, status=200)
        return HttpResponse("Method not allowed", status=405)



@csrf_exempt
def get_chat(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the header
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]  # Remove 'Bearer ' from the token
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user1_nickname = decoded['nickname']
                obj = request.body.decode('utf-8')
                obj = json.loads(obj)
                user2_nickname = obj["user2"]

                if user1_nickname == user2_nickname:
                    return JsonResponse({'error': 'You cannot chat with yourself.'}, status=400)

                # Check if the chat already exists
                existing_chat = Chat.objects.filter(
                    user1__nickname=user1_nickname,
                    user2__nickname=user2_nickname
                ).first()

                existing_chat2 = Chat.objects.filter(
                    user1__nickname=user2_nickname,
                    user2__nickname=user1_nickname
                ).first()

                if existing_chat:
                    return JsonResponse({'chat_id': existing_chat.uid, 'message': 'Chat already exists.'}, status=200)
                if existing_chat2:
                    return JsonResponse({'chat_id': existing_chat2.uid, 'message': 'Chat already exists.'}, status=200)
                # Create a new chat if it doesn't exist
                new_chat = Chat.objects.create_chat(user1_nickname, user2_nickname, f"Chat between {user1_nickname} and {user2_nickname}")
                print(new_chat, '1213123')
                return JsonResponse({'chat_id': new_chat.uid, 'message': 'New chat created.'}, status=201)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.DecodeError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)
            except KeyError as e:
                return JsonResponse({'error': f'Missing parameter: {str(e)}'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def get_user_info(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the header
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]  # Remove 'Bearer ' from the token
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                obj = request.body.decode('utf-8')
                obj = json.loads(obj)
                user = obj["nickname"]


                user = User.objects.get(nickname=user)
            except:
                return JsonResponse({'error': 'Invalid token.'}, status=401)


