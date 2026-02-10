"""
硅基流动AI服务封装模块
用于调用硅基流动的AI接口进行心理状态评分评价
"""

import os
import requests
from typing import Dict, List, Optional
 


class SiliconFlowAIService:
    """硅基流动AI服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI服务
        
        Args:
            api_key: 硅基流动API密钥，如果不提供则从环境变量或settings中获取
        """

        self.base_url = "https://api.siliconflow.cn/v1"
        


        self.model = 'Qwen/Qwen3-VL-32B-Instruct'
        # this model is too slow .
        self.model = "Pro/deepseek-ai/DeepSeek-V3.2"
        self.api_key="sk-fgrddnapdygghksyavgivjnimvxugcgeashotgibhuzbcnrn"

# xulei's key 
        self.api_key = "sk-ovlbuqdmtlbdqgjaorccckeljwkomfsvolukteylzzlzfgcl"


### ali 
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-plus"
        self.api_key = "sk-1065ae7327d84478815f267ef69ca5db" # ali jiao 
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 6000,
        stream: bool = False
    ) -> Dict:
        """
        调用聊天补全接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "system", "content": "..."}, ...]
            temperature: 温度参数，控制随机性，0-1之间
            max_tokens: 最大生成token数
            stream: 是否流式输出
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/chat/completions"
        print(url)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        print(headers)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        print(payload)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            print(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"调用硅基流动AI接口失败: {str(e)}")
    
    def analyze_mental_health(
        self,
        assessment_data: Dict,
        model: Optional[str] = None
    ) -> Dict:
        """
        心理状态评分评价分析
        
        Args:
            assessment_data: 心理评测数据，包含以下字段：
                - title: 评测标题
                - answers: 答案列表
                - scores: 各维度得分
                - total_score: 总分
                - 其他相关信息
            model: 可选，指定使用的模型
        
        Returns:
            包含心理状态评价结果的字典
        """
        if model:
            self.model = model
        
        # 构建系统提示词
        system_prompt = """你是一位专业的心理咨询师和心理评估专家。你需要根据用户提供的心理评测数据，进行全面的心理状态分析和评价。
这是一个标准的scl90心理学评测。

分析维度应包括：
1. 总体心理状态评价（正常/轻度/中度/重度）
2. 各维度得分分析（如躯体化、强迫症状、人际关系敏感等）
3. 主要问题和风险点识别
5. 专业建议和改善方案
6. 是否需要专业心理咨询的建议
7. 总结性评价: summary这个总结字段5000字左右（一定不能少于3000字），总结根据用户的情况根据心理学的理论做出具体的专业分析，并给出专业的医学建议。
   总结是直接给用户看的，所以请一定要按照根据用户需求来写。这个总结不要出现我是ai，字数超过3000字等内容。
   总结最后给出温馨提示：本分析基于SCL-90量表结果，仅为参考。如需更精准评估，建议结合临床访谈、生活背景及生理检查综合判断。如有需要，可联系正规医院心理科或持证心理咨询师进行面谈。
   总结是直接给用户看的，不要出现过多的专业术语，给专业术语要有依据。要避免使用过于负面的语言。要多给正面的鼓励和积极的建议。例如“你有很强的自我觉察力，这是改变的第一步。你不是一个人在战斗。许多人都经历过类似的阶段——情绪波动、孤独、自我怀疑。重要的是，你已经迈出了第一步：看见它，理解它，然后选择改变它。请相信，情绪是可以被调节的，关系是可以被修复的，自我是可以被接纳的。从今天开始，每天给自己一个小小的“心理关怀”：
   总结要注意排版，分成一段一段的，让用户看的舒服。

请以JSON格式返回分析结果，格式如下：
{
    "overall_status": "总体心理状态",
    "severity_level": "严重程度（1-5，1为最轻，5为最重）",
    "dimension_analysis": [
        {"name": "维度名称", "score": 得分, "interpretation": "解释说明"}
    ],
    "key_issues": ["问题1", "问题2"],
    "risk_assessment": "风险评估",
    "recommendations": ["建议1", "建议2"],
    "need_professional_help": true/false,
    "summary": "总结性评价"
}

要求：
- 评价要专业、客观、富有同理心
- 避免使用过于负面的语言
- 提供建设性的建议
- JSON格式必须正确，可以直接解析"""

        # 构建用户消息，组合评测数据
        user_message = self._format_assessment_data(assessment_data)

        # 额外添加原始 JSON 数据，确保 AI 能看到所有字段
        import json
        raw_data_section = "\n\n原始数据（JSON格式）：\n" + json.dumps(assessment_data, ensure_ascii=False, indent=2)
        full_message = user_message
        print(full_message)

        print("\n")
        print("\n")
        print("\n************")
        # print(user_message)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_message}
        ]
        with open('a.log', 'a', encoding='utf-8') as f:
            f.write(str(messages) + '\n')
        # return "{}"
        # 调用AI接口
        response = self.chat_completion(
            messages=messages,
            temperature=0.3,  # 降低温度以获得更稳定的分析
            max_tokens=2000,
            # stream=True
        )
        
        # 提取AI的回复内容
        ai_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(ai_content)
        # 尝试解析JSON格式的分析结果
        import json
        try:
            analysis_result = json.loads(ai_content)
            return {
                "success": True,
                "analysis": analysis_result,
                "raw_response": ai_content
            }
        except json.JSONDecodeError:
            # 如果AI返回的不是标准JSON，则返回原始内容
            return {
                "success": False,
                "error": "AI返回的不是标准JSON格式",
                "raw_response": ai_content
            }
    
    def _format_assessment_data(self, data: Dict) -> str:
        """
        格式化评测数据为自然语言描述（简化版，直接使用前端传来的完整数据）

        Args:
            data: 原始评测数据（包含 title, total_score, scores, questions, data 等字段）

        Returns:
            格式化后的文本描述
        """
        parts = []

        # 添加标题
        if 'title' in data:
            parts.append(f"评测标题：{data['title']}")

        # 添加总分
        if 'total_score' in data:
            parts.append(f"总分：{data['total_score']}")

        # 添加各维度得分
        if 'scores' in data:
            parts.append("\n各维度得分：")
            for dimension, score in data['scores'].items():
                score=str(score)[0:5]
                parts.append(f"{dimension}: {score}")

        # 直接使用前端传来的 questions 数据（包含完整的问题文本和答案描述）
        if 'questions' in data and data['questions']:
            parts.append("\n测试问题和测评人的回答详细情况：")
            for i, q in enumerate(data['questions'], 1):
                parts.append(f"第{i}题: {q['text']}?回答:{q['scoreLabel']},{q['scoreDesc']}.")



        formatted_text = "\n".join(parts)

        
        return formatted_text


def get_ai_service() -> SiliconFlowAIService:
    """
    获取AI服务实例（工厂函数）
    
    Returns:
        SiliconFlowAIService实例
    """
    return SiliconFlowAIService()
