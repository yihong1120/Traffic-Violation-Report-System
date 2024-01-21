from django.urls import path
from . import views, api_views

app_name = 'llm_customer_service'

urlpatterns = [
    # WEB path
    path('chat-with-gemini/', views.chat_with_gemini, name='chat_with_gemini'),

    # API path
    path('api/chat-with-gemini/', api_views.chat_with_gemini_api, name='api_chat_with_gemini'),
]
