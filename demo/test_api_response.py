"""
测试 API 响应格式
用于查看 SiliconFlow API 返回的确切数据结构
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置输出编码为 UTF-8（解决 Windows 控制台编码问题）
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_api_response(audio_file_path, api_key=None):
    """
    测试 API 响应并显示完整的返回数据结构

    Args:
        audio_file_path: 音频文件路径
        api_key: SiliconFlow API Key
    """
    # 获取 API Key
    if not api_key:
        api_key = os.getenv("SILICONFLOW_API_KEY")

    if not api_key:
        print("❌ 错误: 未找到 API Key")
        print()
        print("请通过以下方式之一设置 API Key:")
        print("1. 设置环境变量 SILICONFLOW_API_KEY")
        print("2. 修改此脚本中的 api_key 参数")
        return

    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"❌ 错误: 文件不存在 - {audio_file_path}")
        return

    file_path = Path(audio_file_path)
    print("=" * 60)
    print("API 响应格式测试")
    print("=" * 60)
    print()
    print(f"📁 音频文件: {file_path.name}")
    print(f"📏 文件大小: {file_path.stat().st_size / 1024:.2f} KB")
    print(f"🎤 文件格式: {file_path.suffix}")
    print()

    try:
        # 准备请求数据
        print("🔄 正在调用 API...")
        print()

        files = {
            'file': (file_path.name, open(audio_file_path, 'rb'), 'audio/wav')
        }
        data = {
            'model': 'TeleAI/TeleSpeechASR'
        }
        headers = {
            'Authorization': f'Bearer {api_key}'
        }

        # 发送请求
        response = requests.post(
            'https://api.siliconflow.cn/v1/audio/transcriptions',
            headers=headers,
            files=files,
            data=data
        )

        # 关闭文件
        files['file'][1].close()

        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应状态: {response.reason}")
        print()

        if response.status_code == 200:
            print("=" * 60)
            print("✅ 请求成功")
            print("=" * 60)
            print()

            # 尝试解析 JSON
            try:
                result = response.json()

                print("📊 返回数据结构分析:")
                print("-" * 60)

                # 检查数据类型
                data_type = type(result).__name__
                print(f"数据类型: {data_type}")

                if isinstance(result, dict):
                    print(f"包含字段数: {len(result)}")
                    print(f"字段列表: {', '.join(result.keys())}")
                    print()
                    print("=" * 60)
                    print("完整 JSON 数据:")
                    print("=" * 60)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    print()
                    print("=" * 60)
                    print("字段详细分析:")
                    print("=" * 60)
                    for key, value in result.items():
                        value_type = type(value).__name__
                        print(f"\n字段名: {key}")
                        print(f"  类型: {value_type}")
                        if isinstance(value, str):
                            print(f"  长度: {len(value)} 字符")
                            if len(value) <= 100:
                                print(f"  内容: {value}")
                            else:
                                print(f"  前100字符: {value[:100]}...")
                                print(f"  后100字符: ...{value[-100:]}")
                        elif isinstance(value, (int, float)):
                            print(f"  值: {value}")
                        elif isinstance(value, dict):
                            print(f"  包含字段: {list(value.keys())}")
                        elif isinstance(value, list):
                            print(f"  数组长度: {len(value)}")
                        elif value is None:
                            print(f"  值: null")

                    # 尝试提取文本
                    print()
                    print("=" * 60)
                    print("文本提取尝试:")
                    print("=" * 60)

                    possible_text = (
                        result.get('text') or
                        result.get('transcription') or
                        (result.get('result', {}).get('text') if isinstance(result.get('result'), dict) else None) or
                        (result.get('result', {}).get('transcription') if isinstance(result.get('result'), dict) else None) or
                        (result.get('data', {}).get('text') if isinstance(result.get('data'), dict) else None) or
                        result.get('output')
                    )

                    if possible_text:
                        print(f"✅ 成功提取文本:")
                        print(f"   {possible_text}")
                    else:
                        print("❌ 未能从标准字段中提取文本")
                        print("   请检查上面的字段分析，确定哪个字段包含识别结果")

                elif isinstance(result, str):
                    print(f"字符串长度: {len(result)} 字符")
                    print()
                    print("=" * 60)
                    print("返回内容:")
                    print("=" * 60)
                    print(result)

                else:
                    print("未知的数据类型")

                # 保存原始响应
                output_file = file_path.parent / "api_response_raw.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print()
                print(f"💾 原始响应已保存到: {output_file}")

            except json.JSONDecodeError as e:
                print("❌ JSON 解析失败")
                print(f"错误: {e}")
                print()
                print("原始响应内容:")
                print(response.text)

        else:
            print("=" * 60)
            print("❌ 请求失败")
            print("=" * 60)
            print()
            print(f"HTTP 状态码: {response.status_code}")
            print(f"响应状态: {response.reason}")
            print()

            # 尝试解析错误响应
            try:
                error_data = response.json()
                print("错误响应:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("原始错误响应:")
                print(response.text)

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='测试 API 响应格式')
    parser.add_argument('audio_file', nargs='?', help='音频文件路径')
    parser.add_argument('--api-key', '-k', help='SiliconFlow API Key')
    args = parser.parse_args()

    print()

    if args.audio_file:
        audio_file = args.audio_file
    else:
        demo_dir = Path(__file__).parent
        default_audio = demo_dir / "aa.wav"
        if default_audio.exists():
            audio_file = str(default_audio)
        else:
            audio_file = str(default_audio)

    api_key = args.api_key if args.api_key else None

    test_api_response(audio_file, api_key)

    print()
    print("=" * 60)
    print("提示:")
    print("=" * 60)
    print("1. 查看上面的'返回数据结构分析'部分")
    print("2. 找到包含识别文本的字段名")
    print("3. 如果字段名不在标准列表中，需要修改前端代码")
    print("4. 参考 DEBUG_TRANSCRIPTION.md 文档进行修改")
    print()
