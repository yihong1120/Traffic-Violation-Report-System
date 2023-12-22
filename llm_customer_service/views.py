from django.http import JsonResponse
from .models import Conversation, Prompt
from django.contrib.auth.models import User
import requests
import os

def chat_with_gemini(request):
    user_id = request.GET.get('user_id')
    message = request.GET.get('message')

    # 確保用戶存在
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)

    # 嘗試獲取最新的預設 prompt，如果不存在則使用空字符串
    try:
        default_prompt = Prompt.objects.latest('created_at').text
    except Prompt.DoesNotExist:
        default_prompt = ""  # 或者設定一個預設的 fallback prompt

    # 擷取過往20則對話紀錄作為 prompt
    past_conversations = Conversation.objects.filter(user=user).order_by('-timestamp')[:20]
    conversation_history = "\n".join([f"User: {conv.message}\nBot: {conv.response}" for conv in past_conversations])

    # 組合預設 prompt 和對話歷史
    full_prompt = f"{default_prompt}\n{conversation_history}\nUser: {message}\nBot:"

    # 調用 Gemini API
    response = call_gemini_api(full_prompt)

    # 儲存對話記錄
    Conversation.objects.create(user=user, message=message, response=response)

    return JsonResponse({'response': response})

def call_gemini_api(prompt, message):
    api_key = os.environ.get("GEMINI_API_KEY")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'prompt': prompt + f"\nUser: {message}\nBot:",
        'max_tokens': 150,
    }
    response = requests.post('https://api.gemini.com/v1/chat', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message'].strip()
    else:
        return "Sorry, I can't process your request right now."