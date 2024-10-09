
from django.contrib import admin
from django.urls import path

from profileUser.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/',),
    # path('register/',),
    path('', index)
]
