from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json

from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def register(request):
    if request.method == 'POST':
        obj = request.body.decode('utf-8')
        obj = json.loads(obj)
        nickname = obj["nickname"]
        email = obj["email"]
        role = obj["role"]
        password = obj["password"]

        User = get_user_model()
        try:
            new_user = User.objects.create_user(nickname=nickname, email=email, role=role, password=password)
            new_user.save()

            d = User.objects.get(nickname=nickname)


            return JsonResponse({'token': d.token}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponse("Method not allowed", status=405)