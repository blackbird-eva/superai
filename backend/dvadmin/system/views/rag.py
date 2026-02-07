import os
import requests
import chromadb
from chromadb import PersistentClient
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
from pathlib import Path
from docx import Document

# 导入AI服务
try:
    from ai_service import SiliconFlowAIService
except ImportError:
    # 如果没有ai_service模块，创建一个模拟类
    class SiliconFlowAIService:
        def __init__(self, api_key: str = None):
            self.api_key = api_key or "dummy_key"
        
        def chat_completion(self, messages: List[Dict], **kwargs):
            # 模拟返回
            return {"choices": [{"message": {"content": "这是模拟AI回复"}}]}


class RAGSystem:
    def __init__(self, lm_studio_url: str = "http://127.0.0.1:1234", persist_directory: str = "./chroma_db"):
        """
        初始化RAG系统
        :param lm_studio_url: LM Studio服务器地址
        :param persist_directory: ChromaDB持久化目录
        """
        self.lm_studio_url = lm_studio_url
        # 配置ChromaDB客户端以持久化数据到本地目录
        self.client = PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 检查连接是否可用
        self._test_connection()
        
    def _test_connection(self):
        """测试与LM Studio的连接"""
        try:
            response = requests.get(f"{self.lm_studio_url}/v1/models", timeout=10)
            if response.status_code == 200:
                print("✅ LM Studio连接成功")
            else:
                print(f"❌ LM Studio连接失败，状态码: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到LM Studio，请确保LM Studio正在运行")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用LM Studio获取文本嵌入向量
        :param texts: 要嵌入的文本列表
        :return: 嵌入向量列表
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        embeddings = []
        
        for text in texts:
            payload = {
                "input": text,
                "model": "3e-base-GGUF"  # 使用您提到的模型
            }
            
            response = requests.post(
                f"{self.lm_studio_url}/v1/embeddings",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data['data'][0]['embedding']  # 假设返回格式是这样的
                embeddings.append(embedding)
            else:
                print(f"❌ 获取嵌入失败: {response.status_code}, {response.text}")
                # 返回零向量作为占位符（这可能需要根据实际情况调整）
                embeddings.append([0.0] * 384)  # 假设向量维度是384，根据实际情况调整
        
        return embeddings
    
    def create_collection(self, collection_name: str):
        """
        创建向量集合
        :param collection_name: 集合名称
        """
        try:
            # 尝试获取现有集合，如果不存在则创建
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ 使用现有集合: {collection_name}")
        except:
            self.collection = self.client.create_collection(name=collection_name)
            print(f"✅ 创建新集合: {collection_name}")
    
    def add_documents(self, documents: List[Dict], collection_name: str = "documents"):
        """
        将文档添加到向量数据库
        :param documents: 文档列表，每个文档应包含 'id', 'content', 'metadata' 键
        :param collection_name: 集合名称
        """
        if not hasattr(self, 'collection') or self.collection.name != collection_name:
            self.create_collection(collection_name)
        
        # 获取现有文档的内容列表以避免重复
        existing_data = self.collection.get(include=['documents', 'metadatas'])
        existing_contents = set()
        existing_ids = set()
        
        if 'documents' in existing_data and existing_data['documents']:
            existing_contents.update(existing_data['documents'])
        if 'metadatas' in existing_data and existing_data['metadatas']:
            # 假设在metadata中存储了原始ID
            for metadata in existing_data['metadatas']:
                if 'original_id' in metadata:
                    existing_ids.add(metadata['original_id'])
        
        # 过滤掉已存在的文档（基于内容和ID）
        new_documents = []
        for doc in documents:
            doc_id = doc.get('id', str(uuid.uuid4()))
            doc_content = doc['content']
            
            # 检查内容和ID是否都已存在
            if doc_id not in existing_ids and doc_content not in existing_contents:
                # 为新文档添加原始ID到metadata中，以便后续识别
                new_doc = doc.copy()
                if 'metadata' not in new_doc:
                    new_doc['metadata'] = {}
                new_doc['metadata']['original_id'] = doc_id
                new_documents.append(new_doc)
                # 更新existing_contents集合，防止同一批次内的重复
                existing_contents.add(doc_content)
        
        if not new_documents:
            print("✅ 所有文档都已存在于数据库中，无需添加新文档")
            return
        
        # 提取文本内容用于嵌入
        texts = [doc['content'] for doc in new_documents]
        
        # 获取嵌入向量
        print(f"🔄 正在生成 {len(new_documents)} 个新文档的嵌入向量...")
        embeddings = self.get_embeddings(texts)
        
        # 准备ID、文档内容和元数据
        ids = [doc.get('id', str(uuid.uuid4())) for doc in new_documents]
        metadatas = [doc.get('metadata', {}) for doc in new_documents]
        contents = [doc['content'] for doc in new_documents]
        
        # 添加到ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ 成功添加 {len(new_documents)} 个新文档到集合 '{collection_name}'")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        搜索最相似的文档
        :param query: 查询文本
        :param n_results: 返回结果数量
        :return: 搜索结果
        """
        # 获取查询的嵌入向量
        query_embedding = self.get_embeddings([query])[0]
        
        # 执行相似性搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results['documents'][0])):
            result = {
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else None,
                'id': results['ids'][0][i]
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def list_all_documents(self, collection_name: str = "documents") -> List[Dict]:
        """
        列出向量数据库中所有的文档
        :param collection_name: 集合名称
        :return: 所有文档的列表
        """
        if not hasattr(self, 'collection') or self.collection.name != collection_name:
            self.create_collection(collection_name)
        
        # 获取集合中的所有文档
        all_docs = self.collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        # 格式化结果
        documents_list = []
        for i in range(len(all_docs['documents'])):
            # 检查embeddings是否存在以及是否非空
            embedding_length = 0
            if 'embeddings' in all_docs and all_docs['embeddings'] is not None and len(all_docs['embeddings']) > i:
                embedding_length = len(all_docs['embeddings'][i])
            
            # 检查metadatas是否存在以及是否非空
            metadata = {}
            if 'metadatas' in all_docs and all_docs['metadatas'] is not None and len(all_docs['metadatas']) > i:
                metadata = all_docs['metadatas'][i]
            
            doc_info = {
                'id': all_docs['ids'][i] if ('ids' in all_docs and len(all_docs['ids']) > i) else f'doc_{i}',
                'content': all_docs['documents'][i],
                'metadata': metadata,
                'embedding_length': embedding_length
            }
            documents_list.append(doc_info)
        
        return documents_list
    
    def load_documents_from_folder(self, folder_path: str, file_extensions: List[str] = ['.txt', '.md']) -> List[Dict]:
        """
        从文件夹加载文档
        :param folder_path: 文件夹路径
        :param file_extensions: 要加载的文件扩展名列表
        :return: 文档列表
        """
        folder = Path(folder_path)
        documents = []
        
        for ext in file_extensions:
            for file_path in folder.glob(f"*{ext}"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    document = {
                        'id': str(uuid.uuid4()),
                        'content': content,
                        'metadata': {
                            'source': str(file_path),
                            'filename': file_path.name
                        }
                    }
                    documents.append(document)
        
        return documents
    
    def load_document_from_word(self, file_path: str, min_length: int = 100) -> List[Dict]:
        """
        从Word文档加载大于指定长度的段落
        :param file_path: Word文档路径
        :param min_length: 段落最小长度
        :return: 文档列表
        """
        doc = Document(file_path)
        documents = []
        
        for i, para in enumerate(doc.paragraphs):
            content = para.text.strip()
            if len(content) > min_length:  # 只添加大于指定长度的段落
                document = {
                    'id': f'para_{i}_{str(uuid.uuid4())[:8]}',
                    'content': content,
                    'metadata': {
                        'source': str(file_path),
                        'paragraph_index': i,
                        'length': len(content),
                        'filename': Path(file_path).name
                    }
                }
                documents.append(document)
        
        return documents


def main():
    # 初始化RAG系统，指定向量数据库存储在当前目录
    rag_system = RAGSystem(persist_directory="d:/ai/chroma_db")
    
    # 首先检查tj.docx是否存在
    if os.path.exists("tj.docx"):
        print("📖 发现 tj.docx 文件，正在读取大于100字的段落...")
        word_docs = rag_system.load_document_from_word("tj.docx", min_length=100)
        
        if word_docs:
            print(f"✅ 找到 {len(word_docs)} 个符合条件的段落")
            # 添加文档到向量数据库
            rag_system.add_documents(word_docs, collection_name="tj_docs")
        else:
            print("⚠️ tj.docx 中没有找到大于100字的段落")
    else:
        print("⚠️ 未找到 tj.docx 文件，使用示例文档")
        
        # 示例：添加一些文档
        sample_docs = [
            {
                'id': 'doc1',
                'content': '人工智能是计算机科学的一个分支，它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。',
                'metadata': {
                    'category': 'AI', 
                    'source': 'wiki', 
                    'original_id': 'doc1',
                    'author': 'Wiki Contributor',
                    'date_created': '2024-01-01',
                    'tags': ['AI', 'computer science', 'intelligence'],
                    'business_info': {
                        'department': 'Research',
                        'project': 'AI Study',
                        'priority': 'high'
                    }
                }
            },
            {
                'id': 'doc2',
                'content': '机器学习是人工智能的一个子集，它使计算机能够从数据中学习并做出决策，而无需明确编程。',
                'metadata': {
                    'category': 'ML', 
                    'source': 'wiki', 
                    'original_id': 'doc2',
                    'author': 'Wiki Contributor',
                    'date_created': '2024-01-02',
                    'tags': ['ML', 'data science', 'learning'],
                    'business_info': {
                        'department': 'Data Science',
                        'project': 'ML Basics',
                        'priority': 'medium'
                    }
                }
            },
            {
                'id': 'doc3',
                'content': '深度学习是机器学习的一个分支，使用神经网络模拟人脑的工作方式来解决问题。',
                'metadata': {
                    'category': 'DL', 
                    'source': 'wiki', 
                    'original_id': 'doc3',
                    'author': 'Wiki Contributor',
                    'date_created': '2024-01-03',
                    'tags': ['deep learning', 'neural networks', 'AI'],
                    'business_info': {
                        'department': 'AI Development',
                        'project': 'Neural Networks',
                        'priority': 'high'
                    }
                }
            }
        ]
        
        # 添加文档到向量数据库
        rag_system.add_documents(sample_docs, collection_name="sample_docs")
    
    # 搜索示例
    query = "直升机的发展历史？(我明天开会，需要讲这个问题，请给我总结200字左右，共分四个方面讲)"
    results = rag_system.search(query, n_results=3)  # 获取更多结果用于AI推理
    
    print(f"\n🔍 搜索查询: {query}")
    print("📋 搜索结果:")
    context_texts = []
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document']}")
        print(f"   相似度距离: {result['distance']:.4f}\n")
        context_texts.append(f"相关资料 {i}: {result['document']}")
    
    # 使用AI服务进行推理
    try:
        ai_service = SiliconFlowAIService()
        
        # 构建提示词，结合检索到的上下文
        context_str = "\n".join(context_texts)
        prompt = f"""
        基于以下资料回答问题：
        
        {context_str}
        
        问题：{query}
        
        请根据以上参考资料，给出详细准确的回答。
        """
        
        messages = [
            {"role": "system", "content": "你是一个有用的知识助手，根据给定的参考资料回答用户问题。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用AI服务
        ai_response = ai_service.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        print("🤖 AI推理结果:")
        ai_answer = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "未能获得AI回复")
        print(ai_answer)
        
    except Exception as e:
        print(f"⚠️ 调用AI服务时出错: {e}")
        print("使用本地搜索结果作为替代...")
    # 显示所有文档示例
    return "" 
    print("📚 数据库中的所有文档:")
    collection_name = "tj_docs" if os.path.exists("tj.docx") else "sample_docs"
    all_docs = rag_system.list_all_documents(collection_name=collection_name)
    for i, doc in enumerate(all_docs, 1):
        print(f"{i}. ID: {doc['id']}")
        print(f"   内容: {doc['content'][:100]}...")  # 只显示前100个字符
        print(f"   元数据: {doc['metadata']}")
        print(f"   嵌入向量长度: {doc['embedding_length']}")
        print()


if __name__ == "__main__":
    main()