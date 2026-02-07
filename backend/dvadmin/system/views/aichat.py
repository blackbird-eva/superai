# -*- coding: utf-8 -*-
"""
AI聊天接口
使用RAG系统，基于向量数据库和大模型提供智能问答功能
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # 允许任何用户访问
from datetime import datetime
import json
from .rag import RAGSystem

class AIChatView(APIView):
    """
    AI聊天接口
    接收用户问题，使用RAG系统返回答案
    """
    permission_classes = [AllowAny]  # 允许任何用户访问，无需认证

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化RAG系统，使用已有的向量数据库
        self.rag_system = RAGSystem(persist_directory="d:/ai/chroma_db")
        
        # 检查数据库中有哪些集合，并使用第一个可用的集合
        try:
            collections = self.rag_system.client.list_collections()
            if collections:
                # 使用第一个集合
                collection_name = "sample_docs"
                print(f"📊 数据库中的集合: {[col.name for col in collections]}")
            else:
                # 如果没有集合，使用默认名称
                collection_name = "sample_docs"
                print("⚠️  数据库中没有集合，将使用默认集合: documents")
        except Exception as e:
            # 如果列出集合失败，使用默认名称
            collection_name = "sample_docs"
            print(f"⚠️  无法列出集合，将使用默认集合: {collection_name}, 错误: {str(e)}")
        
        # 创建或获取指定的集合
        collection_name = "tj_docs"
        self.rag_system.create_collection(collection_name)
        print(f"✅ 使用集合: {collection_name}")

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
            
            # 使用RAG系统获取答案
            answer = self.webaichat(question)
            
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

    def webaichat(self, question):
        """
        使用RAG系统回答问题
        :param question: 用户问题
        :return: AI生成的回答
        """
        try:
            # 在向量数据库中搜索相关文档
            search_results = self.rag_system.search(question, n_results=5)  # 获取5个最相关的结果
            
            # 构建上下文
            context_texts = []
            for i, result in enumerate(search_results, 1):
                context_texts.append(f"参考资料 {i}: {result['document']}")
            
            # 如果找到了相关文档，使用它们来生成回答
            if context_texts:
                context_str = "\n".join(context_texts)
                
                # 使用AI服务基于上下文生成回答
                try:
                    from .ai_service import SiliconFlowAIService
                    ai_service = SiliconFlowAIService()
                    
                    # 构建提示词，结合检索到的上下文
                    prompt = f"""
                    基于以下资料回答问题：
                    
                    {context_str}
                    
                    问题: {question}
                    
                    请根据以上参考资料准确回答问题，如果参考资料中没有相关内容，请说明"根据现有资料无法回答该问题"。
                    回答要简洁明了，逻辑清晰。
                    """
                    
                    # 调用AI服务
                    messages = [
                        {"role": "system", "content": "你是一个智能助手，根据提供的参考资料回答用户问题。"},
                        {"role": "user", "content": prompt}
                    ]
                    
                    ai_response = ai_service.chat_completion(messages)
                    
                    # 提取AI生成的回答
                    answer = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "AI未能生成有效回答")
                    
                except Exception as ai_error:
                    # 如果AI服务调用失败，返回检索到的资料
                    print(f"AI服务调用失败: {str(ai_error)}")
                    answer = f"检索到的相关信息：\n{context_str}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                # 如果没有找到相关文档，返回提示信息
                answer = f"在知识库中未找到与问题相关的资料。\n问题: {question}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return answer
            
        except Exception as e:
            # 如果RAG系统出错，返回错误信息
            return f"处理您的问题时出现错误: {str(e)}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"