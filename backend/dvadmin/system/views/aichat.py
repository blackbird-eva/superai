# -*- coding: utf-8 -*-
"""
AI聊天接口
提供简单的问答功能，暂时将问题直接返回作为答案
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # 允许任何用户访问
from datetime import datetime
import json


class AIChatView(APIView):
    """
    AI聊天接口
    接收用户问题，返回答案（暂时直接返回问题内容）
    """


    permission_classes = [AllowAny]  # 允许任何用户访问，无需认证


    def webaichat( self , question):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 暂时将问题直接返回作为答案（加上时间戳用于调试）
        answer = f"[{current_time}] 收到问题: {question}"

        return answer


    def post(self, request):
        """
        处理聊天消息
        :param request: 请求对象，包含question字段
        :return: JSON响应，包含答案
        """
        try:
            # 获取请求数据
            question = request.data.get('question', '').strip()
            
            if not question:
                return Response({
                    'code': 400,
                    'message': '问题不能为空',
                    'data': None
                })
            
            # 获取当前时间用于调试
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 暂时将问题直接返回作为答案（加上时间戳用于调试）
            answer = self.webaichat( question)
            
            # 返回响应
            return Response({
                'code': 2000,
                'message': 'success',
                'data': {
                    'question': question,
                    'answer': answer,
                    'timestamp': current_time
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            })