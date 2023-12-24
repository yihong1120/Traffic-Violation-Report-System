from django.urls import path
from . import views

app_name = 'llm_customer_service'

urlpatterns = [
    path('chat-with-gemini/<int:user_id>/', views.chat_with_gemini, name='chat_with_gemini'),
]
