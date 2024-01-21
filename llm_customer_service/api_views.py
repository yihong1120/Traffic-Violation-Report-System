import json
from .models import Conversation
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .views import call_gemini_api

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_gemini_api(request):
    if request.method == 'POST':
        try:
            user_id = request.user.id
            # 获取用户输入
            user_input = json.loads(request.body).get('message')
            
            # 从数据库获取先前的对话记录
            previous_conversations = Conversation.objects.filter(user_id=user_id).order_by('-timestamp')[:20]
            dialog_history = "\n".join([conv.message + "\n" + conv.response for conv in reversed(previous_conversations)])

            # 调用 Gemini API，传递历史对话和用户输入
            response = call_gemini_api(user_input, dialog_history)

            # 保存新对话到数据库
            new_conversation = Conversation(user_id=user_id, message=user_input, response=response)
            new_conversation.save()

            return Response({'response': response})

        except Exception as e:
            return Response({'error': str(e)})

    return Response({'message': 'This is a POST endpoint.'})