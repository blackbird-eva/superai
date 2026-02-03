# -*- coding: utf-8 -*-
"""
LLM 服务模块
提供统一的调用大模型接口
支持 LM Studio 和其他兼容 OpenAI API 的服务
"""

import requests
import json
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务类"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        # 从配置中读取参数，提供默认值
        self.base_url = getattr(settings, 'LLM_BASE_URL', 'http://localhost:1234/v1')
        self.api_key = getattr(settings, 'LLM_API_KEY', 'not-needed')
        self.model = getattr(settings, 'LLM_MODEL', 'qwen2.5-7b-instruct:2')
        self.temperature = getattr(settings, 'LLM_TEMPERATURE', 0.7)
        self.max_tokens = getattr(settings, 'LLM_MAX_TOKENS', 4000)
        self.timeout = getattr(settings, 'LLM_TIMEOUT', 75)
        
        # 请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"LLM服务初始化: {self.base_url}, 模型: {self.model}")
    
    def _clean_response(self, content: str) -> str:
        """
        清理响应内容，去除 markdown 代码块标记
        
        Args:
            content: 原始响应内容
            
        Returns:
            清理后的内容
        """
        content = content.strip()
        
        # 去除 ```json 或 ```markdown 等标记
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```markdown"):
            content = content[11:]
        elif content.startswith("```python"):
            content = content[10:]
        elif content.startswith("```"):
            content = content[3:]
            
        # 去除结尾的 ```
        if content.endswith("```"):
            content = content[:-3]
            
        return content.strip()
    
    def _chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        调用聊天补全接口
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens等）
            
        Returns:
            API 响应结果
        """
        url = f"{self.base_url}/chat/completions"
        
        # 构建请求参数
        payload = {
            "model": kwargs.get('model', self.model),
            "messages": messages,
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "stream": False
        }
        
        logger.debug(f"LLM请求: {url}")
        logger.debug(f"请求参数: {json.dumps(payload, ensure_ascii=False)[:500]}...")
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"LLM请求超时: {url}")
            raise Exception(f"LLM服务请求超时（{self.timeout}秒）")
        except requests.exceptions.ConnectionError:
            logger.error(f"LLM服务连接失败: {url}")
            raise Exception(f"无法连接到LLM服务: {self.base_url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM请求HTTP错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM服务HTTP错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM请求失败: {str(e)}")
            raise
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        生成响应（基于聊天补全）
        
        Args:
            prompt: 用户输入提示
            system_prompt: 系统提示词（可选）
            
        Returns:
            生成的响应文本
        """
        # 构建消息列表
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            result = self._chat_completion(messages)
            
            # 检查错误
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result["error"]))
                logger.error(f"LLM返回错误: {error_msg}")
                raise Exception(f"LLM服务错误: {error_msg}")
            
            # 提取内容
            if "choices" not in result or len(result["choices"]) == 0:
                logger.error(f"LLM响应格式错误: {result}")
                raise Exception("LLM服务未返回有效内容")
            
            content = result["choices"][0]["message"]["content"]
            
            # 清理响应
            cleaned_content = self._clean_response(content)
            
            logger.info(f"LLM响应成功，内容长度: {len(cleaned_content)}")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"生成响应失败: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        测试 LLM 服务连接
        
        Returns:
            连接是否成功
        """
        try:
            # 发送简单的测试请求
            test_messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            result = self._chat_completion(test_messages, max_tokens=10)
            
            if "choices" in result and len(result["choices"]) > 0:
                logger.info("LLM服务连接测试成功")
                return True
            else:
                logger.error("LLM服务响应格式异常")
                return False
                
        except Exception as e:
            logger.error(f"LLM服务连接测试失败: {str(e)}")
            return False


# 全局单例
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """
    获取 LLM 服务实例（单例模式）
    
    Returns:
        LLMService 实例
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance


def call_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    调用大模型生成响应（简化的接口）
    
    这是 genppt.py 中使用的接口
    
    Args:
        prompt: 用户输入提示
        system_prompt: 系统提示词（可选）
        
    Returns:
        生成的响应文本
        
    Raises:
        Exception: 当调用失败时
        
    示例:
        >>> result = call_llm("请生成一个PPT大纲")
        >>> print(result)
    """
    service = get_llm_service()
    return service.generate_response(prompt, system_prompt)


def is_llm_available() -> bool:
    """
    检查 LLM 服务是否可用
    
    Returns:
        是否可用
    """
    try:
        service = get_llm_service()
        return service.test_connection()
    except Exception as e:
        logger.error(f"检查LLM可用性失败: {str(e)}")
        return False


# 为了向后兼容，保留原有的函数名
def generate_response(prompt: str) -> str:
    """
    生成响应（向后兼容的函数名）
    
    Args:
        prompt: 输入提示文本
        
    Returns:
        生成的响应文本
    """
    return call_llm(prompt)


if __name__ == "__main__":
    """测试代码"""
    print("=" * 60)
    print("LLM 服务测试")
    print("=" * 60)
    
    # 测试连接
    print("\n1. 测试连接...")
    if is_llm_available():
        print("✓ LLM 服务连接成功")
    else:
        print("✗ LLM 服务连接失败")
        exit(1)
    
    # 测试简单生成
    print("\n2. 测试简单生成...")
    try:
        response = call_llm("请用一句话介绍 Python 编程语言")
        print(f"响应: {response}")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    
    # 测试 JSON 生成
    print("\n3. 测试 JSON 生成...")
    json_prompt = """
请生成一个简单的JSON，包含以下字段：
- title: 标题
- items: 3个条目的数组

返回纯JSON格式，不要有其他文字。
"""
    try:
        response = call_llm(json_prompt)
        print(f"响应: {response}")
        
        # 尝试解析
        parsed = json.loads(response)
        print(f"解析成功: {parsed}")
    except Exception as e:
        print(f"✗ JSON 生成或解析失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
