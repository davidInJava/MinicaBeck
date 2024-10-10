
from django.contrib import admin
from django.urls import path

from profileUser.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',authorisation),
    path('register/', register),
    path('authorisation/', authorisation),
    path('find_user/', find_user),
    path('new_chat/', get_chat)
]
