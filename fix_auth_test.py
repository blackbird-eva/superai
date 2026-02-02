#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API认证问题诊断和修复测试
"""

import requests
import json
from datetime import datetime

# 当前使用的API密钥（可能已失效）
OLD_API_KEY = "pat_OpOtxYPsdoqHvzMezDkPm8Lr5U8iZyGhTzfWPtN9aXKfVuBnQjRxZyCmYwSaJtC"

# 测试用的可能的新密钥格式（需要您替换为真实密钥）
# 注意：这只是示例格式，您需要从Coze控制台获取真实的密钥
NEW_API_KEY_EXAMPLE = "pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

BASE_URL = "https://api.coze.cn"
WORKFLOW_ID = "7518128870178832422"
USER_ID = "test_user_001"

def test_api_key(api_key, test_name):
    """测试API密钥"""
    print(f"\n🧪 测试 {test_name}")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试1: 简单的认证测试（如果有用户信息接口）
    print("1. 测试认证头格式...")
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer pat_"):
        print("   ✅ Authorization头格式正确")
    else:
        print("   ❌ Authorization头格式可能错误")
    
    # 测试2: 尝试调用工作流（会触发401或200）
    print("2. 测试工作流调用...")
    url = f"{BASE_URL}/v1/workflow/run"
    payload = {
        "workflow_id": WORKFLOW_ID,
        "parameters": {"input": "测试认证"},
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   🎉 API密钥有效！认证成功")
            return True
        elif response.status_code == 401:
            error_msg = response.json().get('msg', 'Unknown error')
            print(f"   ❌ 认证失败: {error_msg}")
            return False
        else:
            print(f"   ⚠️  其他错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")
        return False

def check_api_key_format(api_key):
    """检查API密钥格式"""
    print(f"\n🔍 检查API密钥格式")
    print("=" * 30)
    
    if not api_key:
        print("   ❌ 密钥为空")
        return False
    
    if not api_key.startswith("pat_"):
        print("   ❌ 密钥应以'pat_'开头")
        return False
    
    if len(api_key) < 20:
        print(f"   ❌ 密钥长度过短: {len(api_key)} 字符")
        return False
    
    print(f"   ✅ 密钥格式正确")
    print(f"   - 前缀: {api_key[:4]}")
    print(f"   - 长度: {len(api_key)} 字符")
    print(f"   - 示例: {api_key[:12]}...{api_key[-8:]}")
    
    return True

def provide_solution_steps():
    """提供解决方案步骤"""
    print(f"\n🛠️  API认证问题解决方案")
    print("=" * 50)
    print("""
📋 步骤1: 获取新的API密钥
   1. 访问 https://www.coze.cn/
   2. 登录您的账户
   3. 点击右上角头像 → "账户设置"
   4. 找到 "API访问" 或 "开发者设置"
   5. 生成新的 Personal Access Token (PAT)
   6. 复制完整的密钥（以pat_开头）

📋 步骤2: 更新代码中的密钥
   将新的密钥替换到代码中：
   
   # 旧的（可能失效）
   API_KEY = "pat_OpOtxYPsdoqHvzMezDkPm8Lr5U8iZyGhTzfWPtN9aXKfVuBnQjRxZyCmYwSaJtC"
   
   # 新的（请替换为真实密钥）
   API_KEY = "pat_your_new_key_here"

📋 步骤3: 检查密钥权限
   确保新密钥有以下权限：
   ✅ 工作流执行权限
   ✅ 文件生成和下载权限
   ✅ 足够的API调用配额

📋 步骤4: 测试连接
   运行此测试脚本验证新密钥
   或直接使用主程序测试
    """)

if __name__ == "__main__":
    print("🔐 Coze API认证问题诊断工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查当前密钥格式
    check_api_key_format(OLD_API_KEY)
    
    # 测试当前密钥
    test_api_key(OLD_API_KEY, "当前API密钥")
    
    # 提供解决方案
    provide_solution_steps()
    
    print(f"\n💡 下一步操作:")
    print("1. 从Coze控制台获取新的API密钥")
    print("2. 更新代码中的API_KEY变量") 
    print("3. 重新运行测试程序")
    print("4. 如需帮助，请提供新的API密钥进行测试")
