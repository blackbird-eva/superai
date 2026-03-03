"""
快速测试脚本
用于快速测试语音转文本功能
"""
import os
from pathlib import Path
from test_transcription import test_transcription, save_result_to_file


def main():
    print("=" * 60)
    print("语音转文本快速测试")
    print("=" * 60)
    print()

    # 检查 demo 目录
    demo_dir = Path(__file__).parent
    audio_file = demo_dir / "aa.wav"

    if not audio_file.exists():
        print(f"❌ 测试文件不存在: {audio_file}")
        print()
        print("请确保以下文件存在:")
        print(f"  - {audio_file}")
        print()
        return

    # 询问使用模式
    print("请选择测试模式:")
    print("  1. 真实 API 模式（需要 API Key 和余额）")
    print("  2. 模拟模式（不需要 API Key，返回模拟结果）")
    print()
    choice = input("请输入选项 (1/2，默认为 2): ").strip()

    if choice == '1':
        # 真实 API 模式
        print()
        print("你选择了真实 API 模式")
        print("=" * 60)
        print()

        # 提示输入 API Key
        print("请输入你的 SiliconFlow API Key:")
        print("(获取地址: https://siliconflow.cn)")
        print()
        api_key = input("API Key: ").strip()

        if not api_key:
            print()
            print("❌ 未输入 API Key")
            print()
            print("提示: 你也可以在 .env 文件中设置 SILICONFLOW_API_KEY")
            print("      或直接修改此脚本中的 api_key 变量")
            return

        print()
        print("=" * 60)

        # 运行测试
        result = test_transcription(str(audio_file), api_key)
    else:
        # 模拟模式
        print()
        print("你选择了模拟模式")
        print("=" * 60)
        print()

        # 运行模拟测试
        result = test_transcription(str(audio_file), mock_mode=True)

    if result:
        print()
        print("=" * 60)
        print("保存结果中...")
        output_file = demo_dir / "transcription_result.txt"
        save_result_to_file(result, str(output_file))
        print()
        print("✅ 测试完成!")
        print(f"📄 结果已保存到: {output_file}")
    else:
        print()
        print("❌ 测试失败")
        print("请检查:")
        print("  1. API Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. API 配额是否充足")
        print()
        print("💡 提示: 可以使用模拟模式进行测试，无需 API Key")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("已取消测试")
    except Exception as e:
        print()
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
