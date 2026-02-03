"""
LM Studio API 接口调用示例
提供对 LM Studio 所有接口的 Python 调用方法
"""

import requests
import json

# LM Studio 配置
BASE_URL = "http://localhost:1234/v1"
API_KEY = "not-needed"  # LM Studio 通常不需要 API Key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_models():
    """
    获取可用模型列表
    GET /v1/models
    """
    url = f"{BASE_URL}/models"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def chat_completion(messages, model="qwen2.5-7b-instruct:2", temperature=0.7, max_tokens=-1, stream=False):
    """
    聊天补全接口
    POST /v1/chat/completions
    
    Args:
        messages (list): 消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        model (str): 模型名称
        temperature (float): 温度参数，控制随机性，范围 0-2
        max_tokens (int): 最大生成令牌数，-1 表示无限制
        stream (bool): 是否流式输出
    
    Returns:
        dict: API 响应结果
    """
    url = f"{BASE_URL}/chat/completions"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def completion(prompt, model="qwen2.5-7b-instruct:2", temperature=0.7, max_tokens=-1, stream=False):
    """
    文本补全接口
    POST /v1/completions
    
    Args:
        prompt (str): 输入提示文本
        model (str): 模型名称
        temperature (float): 温度参数
        max_tokens (int): 最大生成令牌数
        stream (bool): 是否流式输出
    
    Returns:
        dict: API 响应结果
    """
    url = f"{BASE_URL}/completions"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def generate_response(prompt, model="qwen2.5-7b-instruct:2", max_tokens=2000):
    """
    生成响应接口（基于聊天补全）
    注意：/v1/responses 接口可能不被支持，内部使用 /v1/chat/completions

    Args:
        prompt (str): 输入提示文本
        model (str): 模型名称
        max_tokens (int): 最大生成令牌数

    Returns:
        dict: API 响应结果
    """
    # 使用 chat/completions 接口替代
    messages = [
        {"role": "user", "content": prompt}
    ]

    return chat_completion(messages=messages, model=model, temperature=0.7, max_tokens=max_tokens, stream=False)


def create_embeddings(text, model="qwen2.5-7b-instruct:2"):
    """
    创建文本嵌入向量
    POST /v1/embeddings
    
    Args:
        text (str or list): 输入文本或文本列表
        model (str): 模型名称
    
    Returns:
        dict: 包含嵌入向量的 API 响应
    """
    url = f"{BASE_URL}/embeddings"
    
    if isinstance(text, str):
        input_data = text
    else:
        input_data = text
    
    payload = {
        "model": model,
        "input": input_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    """主函数：示例用法"""

    # 调用 generate_response，生成5页PPT的内容
    ppt_prompt = """
请为"Python编程语言介绍"主题生成7页PPT的内容，要求返回JSON格式。
每一页包含：title（标题）和 content（内容，3-5句话）。
其中，第一页是一个总结或概括，引出后面的内容。
倒数第二项是鼓励同学学好这个编程语言，
最后一页是总结或概括，总结前面的内容。
返回的JSON格式如下：
{
  "title": "Python编程语言介绍",
  "pages": [
    {
      "page": 1,
      "title": "页面标题",
      "content": "内容描述，3-5句话"
    },
    ...
  ]
}
"""

    response_result = generate_response(
        prompt=ppt_prompt,
        model="qwen2.5-7b-instruct:2"
    )

    # 提取并解析 content 字段
    if "error" in response_result:
        print(json.dumps(response_result, indent=2, ensure_ascii=False))
        return

    try:
        # 获取 content 字段
        content = response_result["choices"][0]["message"]["content"]

        # 去除 markdown 代码块标记（```json 和 ```）
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        # 解析 JSON
        parsed_json = json.loads(content.strip())

        # 输出解析后的 JSON
        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"解析错误: {e}")
        print("原始内容:")
        print(response_result["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
