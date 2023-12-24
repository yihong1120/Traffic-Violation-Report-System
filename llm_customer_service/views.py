import json
import os
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings

@csrf_exempt
@login_required
def chat_with_gemini(request):
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

            return JsonResponse({'response': response})

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'message': 'This is a POST endpoint.'})


def call_gemini_api(prompt_text, dialog_history):
    # 从环境变量中获取服务账户文件路径
    service_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account_file:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    # 读取服务账户文件内容
    with open(service_account_file) as file:
        service_account_info = json.load(file)
    
    PROJECT_ID = service_account_info["project_id"]
    REGION = service_account_info.get("REGION", "asia-southeast1")

    # 创建凭据对象
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    # 获取访问令牌
    credentials.refresh(Request())
    access_token = credentials.token

    # 构建请求 URL
    url = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/gemini-pro:streamGenerateContent"

    # 构建请求正文，包括历史对话和当前提示
    full_prompt = dialog_history + "\n" + prompt_text
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": full_prompt
            }]
        }],
        "safety_settings": {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_LOW_AND_ABOVE"
        },
        "generation_config": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 2560,
            # "stopSequences": [".", "?", "!"]
        }
    }

    # 发送请求
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        },
        data=json.dumps(payload)
    )

    # 检查响应并提取文本
    response_data = response.json()
    texts = []
    for candidate in response_data:
        for content in candidate.get('candidates', []):
            for part in content.get('content', {}).get('parts', []):
                texts.append(part.get('text', ''))

    # 将所有文本组合成一个字符串
    return ' '.join(texts)