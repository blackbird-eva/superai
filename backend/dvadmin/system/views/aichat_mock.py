from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings


class AIChatView(APIView):
    permission_classes = [AllowAny]  # 允许匿名访问
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 从配置文件中获取 API Key 和模型
        self.api_key = getattr(settings, 'SILICONFLOW_API_KEY', '')
        self.model = getattr(settings, 'SILICONFLOW_MODEL', 'THUDM/glm-4-9b-chat')
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
    
    def post(self, request):
        # 兼容前端发送的字段名（question 或 message）
        message = request.data.get('message', '') or request.data.get('question', '')
        session_id = request.data.get('session_id', 'mock_session')
        
        # 如果没有 API Key，返回提示信息
        if not self.api_key:
            response_data = {
                'code': 2000,
                'msg': 'success',
                'data': {
                    'answer': '请先在 conf/env.py 中配置硅基流动 API Key (SILICONFLOW_API_KEY)',
                    'session_id': session_id
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        try:
            # 调用硅基流动 API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": message}
                ],
                "stream": False,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 获取回复内容
            ai_message = result['choices'][0]['message']['content']
            
            response_data = {
                'code': 2000,
                'msg': 'success',
                'data': {
                    'answer': ai_message,
                    'session_id': session_id
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            # 错误处理
            error_message = f"API 调用失败: {str(e)}"
            response_data = {
                'code': 2000,
                'msg': 'success',
                'data': {
                    'answer': error_message,
                    'session_id': session_id
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

