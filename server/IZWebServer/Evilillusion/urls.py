from django.contrib import admin
from django.urls import path, re_path, include
from Evilillusion.views import index, search, login, redirect_to

urlpatterns = [
    path('', index, name='index'),
    path('webhp', index),
    path('m', index),
    path('search', search, name='search'),
    re_path('login*', login, name='login'),
    path('url', redirect_to, name="redirect_to"),
]