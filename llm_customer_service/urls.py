from django.urls import path
from . import views

app_name = 'llm_customer_service'

urlpatterns = [
    path('chat-with-gemini/', views.chat_with_gemini, name='chat_with_gemini'),
]
