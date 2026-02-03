#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM 服务测试脚本
验证 llm_service.py 的实现是否合理
"""

import sys
import os
import django

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dvadmin.settings')
django.setup()

import json
from dvadmin.utils.llm_service import (
    call_llm,
    is_llm_available,
    get_llm_service
)


def test_connection():
    """测试1：连接测试"""
    print("\n" + "=" * 60)
    print("测试1：LLM 服务连接")
    print("=" * 60)
    
    try:
        available = is_llm_available()
        if available:
            print("✓ LLM 服务连接成功")
            return True
        else:
            print("✗ LLM 服务连接失败")
            return False
    except Exception as e:
        print(f"✗ 连接测试异常: {e}")
        return False


def test_simple_generation():
    """测试2：简单文本生成"""
    print("\n" + "=" * 60)
    print("测试2：简单文本生成")
    print("=" * 60)
    
    prompt = "请用一句话介绍 Python 编程语言。"
    
    try:
        print(f"提示词: {prompt}")
        response = call_llm(prompt)
        print(f"响应: {response}")
        print("✓ 简单生成成功")
        return True
    except Exception as e:
        print(f"✗ 简单生成失败: {e}")
        return False


def test_json_generation():
    """测试3：JSON 格式生成"""
    print("\n" + "=" * 60)
    print("测试3：JSON 格式生成")
    print("=" * 60)
    
    prompt = """
请生成一个简单的JSON，包含以下字段：
- title: "Python编程"
- items: 包含3个编程概念的数组

要求：
1. 返回纯JSON格式
2. 不要有任何其他文字说明
3. 使用 ```json 或 ``` 标记都可以
"""
    
    try:
        print(f"提示词: {prompt[:100]}...")
        response = call_llm(prompt)
        print(f"原始响应: {response}")
        
        # 尝试解析 JSON
        parsed = json.loads(response)
        print(f"\n解析结果:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        
        # 验证字段
        if "title" in parsed and "items" in parsed:
            print(f"\n✓ JSON 生成和解析成功")
            print(f"  - title: {parsed['title']}")
            print(f"  - items 数量: {len(parsed['items'])}")
            return True
        else:
            print(f"\n✗ JSON 结构不正确")
            return False
            
    except json.JSONDecodeError as e:
        print(f"✗ JSON 解析失败: {e}")
        print(f"原始内容: {response}")
        return False
    except Exception as e:
        print(f"✗ JSON 生成失败: {e}")
        return False


def test_ppt_outline_generation():
    """测试4：PPT大纲生成（模拟 genppt.py 的使用）"""
    print("\n" + "=" * 60)
    print("测试4：PPT大纲生成（模拟 genppt.py 调用）")
    print("=" * 60)
    
    text_content = """
Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
Python的设计哲学强调代码的可读性和简洁的语法，尤其是使用显著的缩进。
Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
Python拥有一个庞大而丰富的标准库，涵盖了各种任务。
Python在数据科学、人工智能、Web开发等领域有广泛应用。
    """.strip()
    
    prompt = f"""
请分析以下文本内容，为PPT生成3页幻灯片的结构化内容。

主题风格：business
语言：中文

原始文本内容：
{text_content}

请按照以下JSON格式返回内容：
{{
    "slides": [
        {{
            "type": "bullet_points",
            "title": "幻灯片标题",
            "content": ["要点1", "要点2", "要点3"],
            "note": "备注信息"
        }}
    ]
}}

注意：
1. 幻灯片类型包括：bullet_points（要点列表）、two_column（双栏）、chart（图表）、summary（总结）
2. 确保内容简洁、专业
3. 每个要点不超过50个字
4. 返回纯JSON格式，不要有其他说明文字
"""
    
    try:
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"文本内容长度: {len(text_content)} 字符")
        
        llm_response = call_llm(prompt)
        print(f"\n响应长度: {len(llm_response)} 字符")
        print(f"响应预览: {llm_response[:200]}...")
        
        # 解析返回的JSON
        ai_content = json.loads(llm_response)
        
        # 验证结构
        if "slides" not in ai_content:
            print("\n✗ 缺少 'slides' 字段")
            return False
        
        slides = ai_content["slides"]
        print(f"\n✓ 大模型成功生成内容，共{len(slides)}页")
        
        # 打印每页内容
        for i, slide in enumerate(slides, 1):
            print(f"\n第{i}页:")
            print(f"  类型: {slide.get('type')}")
            print(f"  标题: {slide.get('title')}")
            content = slide.get('content', [])
            if isinstance(content, list):
                print(f"  要点数: {len(content)}")
                for j, item in enumerate(content[:3], 1):
                    print(f"    {j}. {item}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON 解析失败: {e}")
        print(f"原始内容: {llm_response[:500]}")
        return False
    except Exception as e:
        print(f"\n✗ PPT大纲生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试5：错误处理"""
    print("\n" + "=" * 60)
    print("测试5：错误处理")
    print("=" * 60)
    
    # 测试超长文本
    long_prompt = "请生成" + "A" * 100000 + "的内容"
    
    try:
        print("测试超长文本...")
        response = call_llm(long_prompt)
        print(f"✗ 应该抛出异常但没有")
        return False
    except Exception as e:
        print(f"✓ 正确捕获异常: {type(e).__name__}")
        print(f"  错误信息: {str(e)[:100]}")
        return True


def test_markdown_cleaning():
    """测试6：Markdown标记清理"""
    print("\n" + "=" * 60)
    print("测试6：Markdown标记清理")
    print("=" * 60)
    
    service = get_llm_service()
    
    # 测试不同格式的响应
    test_cases = [
        ("```json\n{\"test\": 1}\n```", '{"test": 1}'),
        ("```\n{\"test\": 2}\n```", '{"test": 2}'),
        ("{\"test\": 3}", '{"test": 3}'),
    ]
    
    all_passed = True
    for raw, expected in test_cases:
        cleaned = service._clean_response(raw)
        if cleaned == expected:
            print(f"✓ 清理成功: {raw[:30]}... -> {cleaned}")
        else:
            print(f"✗ 清理失败: {raw[:30]}... -> {cleaned} (期望: {expected})")
            all_passed = False
    
    return all_passed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("LLM 服务合理性验证测试")
    print("=" * 60)
    
    # 从配置中读取设置
    from django.conf import settings
    use_llm = getattr(settings, 'USE_LLM_FOR_PPT', False)
    base_url = getattr(settings, 'LLM_BASE_URL', 'http://localhost:1234/v1')
    model = getattr(settings, 'LLM_MODEL', 'unknown')
    
    print(f"\n配置信息:")
    print(f"  USE_LLM_FOR_PPT: {use_llm}")
    print(f"  LLM_BASE_URL: {base_url}")
    print(f"  LLM_MODEL: {model}")
    
    # 如果未启用 LLM，给出提示
    if not use_llm:
        print("\n⚠️  警告: USE_LLM_FOR_PPT = False")
        print("   建议在 settings.py 中设置为 True 以启用大模型功能")
        print("   当前测试将使用默认配置继续...")
    
    # 运行所有测试
    tests = [
        ("连接测试", test_connection),
        ("简单生成", test_simple_generation),
        ("JSON生成", test_json_generation),
        ("PPT大纲生成", test_ppt_outline_generation),
        ("错误处理", test_error_handling),
        ("Markdown清理", test_markdown_cleaning),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\n测试中断")
            break
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 异常: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # 打印测试结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 所有测试通过！llm_service.py 实现合理。")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
