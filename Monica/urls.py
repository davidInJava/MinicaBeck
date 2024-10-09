
from django.contrib import admin
from django.urls import path

from profileUser.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',get_user),
    path('register/', register),
    path('', index)
]
