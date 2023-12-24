import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# 配置您的项目和服务帐户信息
PROJECT_ID = ""
REGION = "asia-southeast1" ## Singapour
SERVICE_ACCOUNT_FILE = ""

# 创建凭据对象
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# 获取访问令牌
credentials.refresh(Request())
access_token = credentials.token

# 构建请求 URL
url = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/gemini-pro:streamGenerateContent"

# 构建请求正文
payload = {
    "contents": [{
        "role": "user",
        "parts": [{
            "text": "台灣警方路口（非車輛）大量裝設紅藍色的爆閃燈，有違法嗎？"
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

# 打印响应
print(response.json())
"""
[{'candidates': [{'content': {'role': 'model', 'parts': [{'text': '台灣警方路口（非車輛）大量裝設紅藍色的爆'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'LOW'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '閃燈，是否違法取決於具體情況。\n\n1.'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': ' **合法情況**：\n   - 警方在執行交通管制或其他執法任務時，可以使用爆閃燈來警示駕駛人'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'LOW'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '或行人。\n   - 警方在路口設置爆閃燈，以提醒駕駛人注意路口安全，防止交通事故。\n'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '   - 警方在路口設置爆閃燈，以引導行人安全通過路口。\n\n2. **違法情況**：\n   - 警方在非執行交通管制或其他執法任務時'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '，使用爆閃燈。\n   - 警方在路口設置爆閃燈，但沒有明確的警示標誌或指示牌，導致駕駛人或行人誤會或混淆。\n   - '}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '警方在路口設置爆閃燈，但爆閃燈的光線過於刺眼或閃爍頻率過快，導致駕駛人或行人視覺疲勞或眩暈。\n\n因此，台灣警方路口（非車輛）大量裝設紅藍色的爆閃燈，是否違法'}]}, 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}]}, {'candidates': [{'content': {'role': 'model', 'parts': [{'text': '取決於具體情況。如果警方在執行交通管制或其他執法任務時，使用爆閃燈來警示駕駛人或行人，則不違法。如果警方在非執行交通管制或其他執法任務時，使用爆閃燈，則可能違法。'}]}, 'finishReason': 'STOP', 'safetyRatings': [{'category': 'HARM_CATEGORY_HARASSMENT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability': 'NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'NEGLIGIBLE'}]}], 'usageMetadata': {'promptTokenCount': 24, 'candidatesTokenCount': 324, 'totalTokenCount': 348}}]
"""