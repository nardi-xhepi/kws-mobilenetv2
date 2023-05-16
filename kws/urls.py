from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sendAudio', views.send_audio, name='audio'),
]
