from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Conversation, Prompt
from unittest.mock import patch
import json

class LLMCustomerServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'password': '12345'}
        )

    def test_chat_with_nonexistent_user(self):
        response = self.client.get('/chat/', {'user_id': '999', 'message': 'Hello'})
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'User does not exist')  # 验证错误信息

    def test_chat_with_no_default_prompt(self):
        self.client.force_login(self.user)
        response = self.client.get('/chat/', {'user_id': self.user.id, 'message': 'Hello'})
        self.assertNotEqual(response.status_code, 404) 

    @patch('llm_customer_service.views.call_gemini_api')
    def test_chat_with_gemini_api(self, mock_call_gemini_api):
        mock_call_gemini_api.return_value = 'Hi there!'

        self.client.force_login(self.user)
        response = self.client.get('/chat/', {'user_id': self.user.id, 'message': 'Hello'})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['response'], 'Hi there!')

        conversation = Conversation.objects.last()
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.message, 'Hello')
        self.assertEqual(conversation.response, 'Hi there!')
