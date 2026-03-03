"""
简单的 API 测试脚本
直接在这里填入您的 API Key
"""
import requests
import json
from pathlib import Path

# ===========================
# 请在这里填入您的 API Key
# ===========================
API_KEY = "sk-nauzyucjkvkjocjmnnknfyjpxjcteygeyazqfwckhfpkwpzx"  # ← 替换为您的真实 API Key
# ===========================

# 音频文件路径
AUDIO_FILE = Path(__file__).parent / "aa.wav"

if API_KEY == "YOUR_API_KEY_HERE":
    print("=" * 60)
    print("❌ 请先设置 API Key")
    print("=" * 60)
    print()
    print("请打开这个文件，找到 API_KEY 变量")
    print("把 'YOUR_API_KEY_HERE' 替换为您的真实 API Key")
    print()
    print("您的 API Key 可以在以下地方获取:")
    print("  1. 浏览器页面的设置中查看")
    print("  2. SiliconFlow 官网控制台: https://cloud.siliconflow.cn")
    print()
else:
    print("=" * 60)
    print("API 响应测试")
    print("=" * 60)
    print()
    print(f"📁 音频文件: {AUDIO_FILE.name}")
    print(f"📏 文件大小: {AUDIO_FILE.stat().st_size / 1024:.2f} KB")
    print()

    try:
        print("🔄 正在调用 API...")
        print()

        files = {
            'file': (AUDIO_FILE.name, open(AUDIO_FILE, 'rb'), 'audio/wav')
        }
        data = {
            'model': 'TeleAI/TeleSpeechASR'
        }
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }

        response = requests.post(
            'https://api.siliconflow.cn/v1/audio/transcriptions',
            headers=headers,
            files=files,
            data=data
        )

        files['file'][1].close()

        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应状态: {response.reason}")
        print()

        if response.status_code == 200:
            print("=" * 60)
            print("✅ 请求成功")
            print("=" * 60)
            print()

            result = response.json()

            print("=" * 60)
            print("📊 完整返回数据:")
            print("=" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print()

            print("=" * 60)
            print("📋 字段分析:")
            print("=" * 60)

            if isinstance(result, dict):
                print(f"包含字段: {', '.join(result.keys())}")
                print()

                print("=" * 60)
                print("🔍 文本提取尝试:")
                print("=" * 60)

                # 检查各种可能的字段
                checks = [
                    ('text', result.get('text')),
                    ('transcription', result.get('transcription')),
                    ('result.text', result.get('result', {}).get('text')),
                    ('result.transcription', result.get('result', {}).get('transcription')),
                    ('data.text', result.get('data', {}).get('text')),
                    ('data.transcription', result.get('data', {}).get('transcription')),
                    ('output', result.get('output')),
                ]

                found = False
                for field_path, value in checks:
                    if value and isinstance(value, str) and value.strip():
                        print(f"✅ 找到识别文本 ({field_path}):")
                        print(f"   {value}")
                        found = True
                        break

                if not found:
                    print("❌ 在标准字段中未找到识别文本")
                    print()
                    print("所有字段及其内容:")
                    for key, value in result.items():
                        print(f"\n  {key}:")
                        if isinstance(value, str):
                            print(f"    类型: string")
                            print(f"    长度: {len(value)}")
                            print(f"    内容: {value[:100]}..." if len(value) > 100 else f"    内容: {value}")
                        elif isinstance(value, (int, float)):
                            print(f"    类型: {type(value).__name__}")
                            print(f"    值: {value}")
                        elif isinstance(value, dict):
                            print(f"    类型: dict")
                            print(f"    包含字段: {list(value.keys())}")
                        elif isinstance(value, list):
                            print(f"    类型: list")
                            print(f"    长度: {len(value)}")
                        else:
                            print(f"    类型: {type(value).__name__}")

            # 保存响应
            output_file = AUDIO_FILE.parent / "api_response.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print()
            print(f"💾 响应已保存到: {output_file}")

        else:
            print("=" * 60)
            print("❌ 请求失败")
            print("=" * 60)
            print()
            print(f"HTTP 状态码: {response.status_code}")

            try:
                error_data = response.json()
                print("错误信息:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("原始响应:")
                print(response.text)

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("💡 提示:")
    print("=" * 60)
    print("1. 查看'完整返回数据'部分")
    print("2. 查看'字段分析'部分")
    print("3. 如果未找到文本，查看'所有字段及其内容'")
    print("4. 把包含识别文本的字段名告诉我")
    print()
