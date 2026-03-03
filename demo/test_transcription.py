"""
测试 SiliconFlow 语音转文本 API
使用 TeleAI/TeleSpeechASR 模型进行语音识别
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# 设置输出编码为 UTF-8（解决 Windows 控制台编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载环境变量
load_dotenv()

# SiliconFlow API 配置
API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
MODEL = "TeleAI/TeleSpeechASR"


def test_transcription(audio_file_path, api_key=None, mock_mode=False):
    """
    测试语音转文本功能

    Args:
        audio_file_path: 音频文件路径
        api_key: SiliconFlow API Key，如果不提供则从环境变量读取
        mock_mode: 是否使用模拟模式（不调用真实 API）
    """
    # 模拟模式
    if mock_mode:
        print("🔧 使用模拟模式（不调用真实 API）")
        print()

        # 获取文件信息
        file_path = Path(audio_file_path)
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"📁 音频文件: {file_path.name}")
            print(f"📏 文件大小: {file_size / 1024:.2f} KB")
            print(f"🎤 文件格式: {file_path.suffix}")
            print()
        else:
            print(f"⚠️  文件不存在，使用纯模拟模式: {audio_file_path}")
            print()

        # 模拟 API 调用延迟
        print("🔄 模拟 API 调用中...")
        import time
        time.sleep(2)  # 模拟延迟

        # 模拟识别结果
        mock_result = {
            'text': '形成超多方言语音识别大模型是业内首个，同时支持普通话英文50。种方言自由混说的语言识别大模型模型支持粤语上海话四川话等主要方言。模型设计蒸馏加蒸膨胀联合训练解决多种场景海量数据训练探索方问题。',
            'duration': 10.0
        }

        print("✅ 模拟识别成功!")
        print()
        print("=" * 60)
        print("识别结果:")
        print("=" * 60)
        print(mock_result.get('text', ''))
        print("=" * 60)
        print()
        print(f"⏱️  音频时长: {mock_result.get('duration', 0):.2f} 秒")
        print()
        print("💡 提示: 这是模拟结果，实际使用时会调用真实 API")
        print()

        return mock_result

    # 真实 API 调用模式
    # 获取 API Key
    if not api_key:
        api_key = os.getenv("SILICONFLOW_API_KEY")

    if not api_key:
        print("❌ 错误: 未找到 API Key")
        print("请通过以下方式之一设置 API Key:")
        print("1. 设置环境变量 SILICONFLOW_API_KEY")
        print("2. 直接传入 api_key 参数")
        print("3. 使用 --mock 参数进入模拟模式")
        return None
    
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"❌ 错误: 文件不存在 - {audio_file_path}")
        return None
    
    # 获取文件信息
    file_path = Path(audio_file_path)
    file_size = file_path.stat().st_size
    print(f"📁 音频文件: {file_path.name}")
    print(f"📏 文件大小: {file_size / 1024:.2f} KB")
    print(f"🎤 文件格式: {file_path.suffix}")
    print()
    
    try:
        # 准备请求数据
        print("🔄 正在调用 API...")
        files = {
            'file': (file_path.name, open(audio_file_path, 'rb'), 'audio/wav')
        }
        data = {
            'model': MODEL
        }
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # 发送请求
        response = requests.post(API_URL, headers=headers, files=files, data=data)
        
        # 关闭文件
        files['file'][1].close()
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 请求成功!")
            print()
            print("=" * 60)
            print("识别结果:")
            print("=" * 60)
            print(result.get('text', ''))
            print("=" * 60)
            print()
            
            # 打印详细信息
            if 'duration' in result:
                print(f"⏱️  音频时长: {result['duration']:.2f} 秒")
            
            return result
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_files(audio_files, api_key=None):
    """
    测试多个音频文件的转录

    Args:
        audio_files: 音频文件路径列表
        api_key: SiliconFlow API Key
    """
    print("=" * 60)
    print("批量语音转文本测试")
    print("=" * 60)
    print()
    
    results = []
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[测试 {i}/{len(audio_files)}]")
        print("-" * 60)
        result = test_transcription(audio_file, api_key)
        if result:
            results.append({
                'file': audio_file,
                'result': result
            })
        print()
    
    # 汇总
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"总计: {len(audio_files)} 个文件")
    print(f"成功: {len(results)} 个文件")
    print(f"失败: {len(audio_files) - len(results)} 个文件")
    print()
    
    return results


def save_result_to_file(result, output_file):
    """
    将转录结果保存到文件

    Args:
        result: 转录结果
        output_file: 输出文件路径
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 语音转文本结果\n")
            f.write(f"# 模型: {MODEL}\n")
            f.write(f"# 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(result.get('text', ''))
        
        print(f"💾 结果已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    import argparse

    print("=" * 60)
    print("SiliconFlow 语音转文本测试工具")
    print("=" * 60)
    print()

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='语音转文本测试工具')
    parser.add_argument('audio_file', nargs='?', help='音频文件路径')
    parser.add_argument('--api-key', '-k', help='SiliconFlow API Key')
    parser.add_argument('--mock', '-m', action='store_true', help='使用模拟模式（不调用真实 API）')
    args = parser.parse_args()

    # 确定使用模式
    mock_mode = args.mock

    # 确定音频文件
    if args.audio_file:
        audio_file = args.audio_file
    else:
        demo_dir = Path(__file__).parent
        default_audio = demo_dir / "aa.wav"
        if default_audio.exists():
            audio_file = str(default_audio)
            print(f"使用默认测试文件: {default_audio}")
            print()
        else:
            audio_file = str(default_audio)

    # 确定使用的 API Key（如果不是模拟模式）
    api_key = args.api_key if args.api_key else None

    # 运行测试
    result = test_transcription(audio_file, api_key, mock_mode)

    if result:
        # 自动保存结果
        if os.path.exists(audio_file):
            output_file = os.path.splitext(audio_file)[0] + '_result.txt'
        else:
            output_file = Path(__file__).parent / "transcription_result.txt"

        save_result_to_file(result, str(output_file))
    elif not mock_mode:
        # 如果真实模式失败，提示使用模拟模式
        print()
        print("💡 提示: 如果账户余额不足或没有 API Key，可以使用模拟模式:")
        print(f"  python {sys.argv[0]} --mock")
        print(f"  python {sys.argv[0]} --audio-file aa.wav --mock")
        print()
