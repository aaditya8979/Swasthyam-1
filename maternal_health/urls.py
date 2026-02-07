"""
URL patterns for the maternal health app.
"""

from django.urls import path
from . import views

app_name = 'maternal_health'

urlpatterns = [
    path('', views.maternal_home_view, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/rate-chat/', views.rate_chat, name='rate_chat'),
    path('history/', views.chat_history_view, name='chat_history'),
]