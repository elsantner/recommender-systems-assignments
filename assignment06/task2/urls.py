from django.urls import path

from . import views

app_name = 'task2'

urlpatterns = [
    path('', views.index, name='index'),
    path('recommendation/', views.result, name='recommendation')
]
