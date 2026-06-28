#!/usr/bin/env python3
"""基础使用示例

演示 Xiaoyi SDK 的基本功能：
- 流式对话
- 获取完整响应
- 多轮对话
- 思维链显示
"""

import sys
from pathlib import Path

# 添加 src 目录到路径（用于开发测试）
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xiaoyi_sdk import (
    XiaoyiAI,
    XiaoyiSession,
    SSEMessage,
    IncrementalTracker,
    generate_anonymous_id,
    QuotaExceededError,
)


def example_streaming_chat():
    """示例1：流式对话"""
    print("=" * 50)
    print("示例1：流式对话")
    print("=" * 50)

    ai = XiaoyiAI()

    question = "鸿蒙系统有什么优势？"
    print(f"提问: {question}")
    print("回答: ", end="", flush=True)

    try:
        for chunk in ai.chat(question):
            # 解析SSE数据
            msg = SSEMessage(chunk)

            if msg.is_error:
                print(f"\n错误: {msg.error_message}")
                break

            if msg.has_text:
                # 注意：streamingText 是累积式的，需要提取增量
                # 这里简化处理，直接打印最新文本
                print(msg.text_chunk, end="", flush=True)

            if msg.is_final:
                print("\n[对话结束]")
                break

    except QuotaExceededError as e:
        print(f"\n额度已用完: {e}")

    print()


def example_full_response():
    """示例2：获取完整响应"""
    print("=" * 50)
    print("示例2：获取完整响应")
    print("=" * 50)

    ai = XiaoyiAI()

    question = "华为云有哪些核心服务？"
    print(f"提问: {question}")

    try:
        response = ai.chat_with_response(question)

        print(f"\n完整回答:\n{response.response}")
        print(f"\n对话ID: {response.dialog_id}")
        print(f"设备ID: {response.anonymous_id}")

        if response.has_references:
            print(f"\n引用来源 ({len(response.references)} 个):")
            for ref in response.references[:3]:  # 只显示前3个
                print(f"  - {ref}")

    except Exception as e:
        print(f"错误: {e}")

    print()


def example_incremental_tracker():
    """示例3：使用增量追踪器"""
    print("=" * 50)
    print("示例3：使用增量追踪器")
    print("=" * 50)

    ai = XiaoyiAI()
    tracker = IncrementalTracker()

    question = "ArkTS语言有什么特点？"
    print(f"提问: {question}")
    print("回答: ", end="", flush=True)

    try:
        for chunk in ai.chat(question):
            msg = SSEMessage(chunk)

            if msg.is_error:
                print(f"\n错误: {msg.error_message}")
                break

            if msg.has_text:
                # 使用追踪器提取增量文本
                delta = tracker.new_text(msg)
                if delta:
                    print(delta, end="", flush=True)

            if msg.is_final:
                print("\n[对话结束]")
                break

    except QuotaExceededError as e:
        print(f"\n额度已用完: {e}")

    print()


def example_multi_round_chat():
    """示例4：多轮对话"""
    print("=" * 50)
    print("示例4：多轮对话")
    print("=" * 50)

    ai = XiaoyiAI()
    tracker = IncrementalTracker()

    questions = [
        "什么是鸿蒙系统？",
        "它有什么特点？",
        "适合什么场景？",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n第{i}轮提问: {question}")
        print("回答: ", end="", flush=True)

        tracker.reset()  # 每轮重置追踪器

        try:
            for chunk in ai.chat(question):
                msg = SSEMessage(chunk)

                if msg.is_error:
                    print(f"\n错误: {msg.error_message}")
                    break

                if msg.has_text:
                    delta = tracker.new_text(msg)
                    if delta:
                        print(delta, end="", flush=True)

                if msg.is_final:
                    print()
                    break

        except QuotaExceededError as e:
            print(f"\n额度已用完: {e}")
            break

    print(f"\n当前对话轮次: {ai.round_number}")


def example_thinking_chain():
    """示例5：思维链显示"""
    print("=" * 50)
    print("示例5：思维链显示（深度思考模式）")
    print("=" * 50)

    ai = XiaoyiAI()

    question = "如何设计一个高并发系统？"
    print(f"提问: {question}")

    try:
        response = ai.chat_with_response(question, show_thinking=True)

        if response.thinking:
            print("\n=== 思维链 ===")
            print(response.thinking[:500])  # 只显示前500字符

        print("\n=== 回答 ===")
        print(response.response[:500])  # 只显示前500字符

    except Exception as e:
        print(f"错误: {e}")

    print()


def example_session_api():
    """示例6：底层会话API"""
    print("=" * 50)
    print("示例6：底层会话API")
    print("=" * 50)

    session = XiaoyiSession()
    tracker = IncrementalTracker()

    print(f"设备ID: {session.anonymous_id}")

    # 创建对话
    dialog_id = session.create_dialog()
    print(f"对话ID: {dialog_id}")

    # 首轮提问
    question = "介绍一下华为DevEco Studio"
    print(f"\n提问: {question}")
    print("回答: ", end="", flush=True)

    try:
        for chunk in session.ask(question, sub_type=2):  # 首轮用sub_type=2
            msg = SSEMessage(chunk)

            if msg.is_error:
                print(f"\n错误: {msg.error_message}")
                break

            if msg.has_text:
                delta = tracker.new_text(msg)
                if delta:
                    print(delta, end="", flush=True)

            if msg.is_final:
                print()
                break

    except Exception as e:
        print(f"错误: {e}")

    session.close()
    print("\n会话已关闭")


def example_custom_device_id():
    """示例7：自定义设备ID"""
    print("=" * 50)
    print("示例7：自定义设备ID")
    print("=" * 50)

    # 使用种子生成确定性ID
    custom_id = generate_anonymous_id("my_custom_seed_123")
    print(f"自定义设备ID: {custom_id}")

    ai = XiaoyiAI(anonymous_id=custom_id)

    question = "华为开源社区有哪些项目？"
    print(f"提问: {question}")

    try:
        response = ai.chat_with_response(question)
        print(f"\n回答:\n{response.response[:300]}...")
        print(f"\n使用设备ID: {response.anonymous_id}")

    except Exception as e:
        print(f"错误: {e}")

    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Xiaoyi SDK 基础使用示例")
    print("=" * 60 + "\n")

    # 选择性运行示例
    examples = [
        ("流式对话", example_streaming_chat),
        ("完整响应", example_full_response),
        ("增量追踪器", example_incremental_tracker),
        ("多轮对话", example_multi_round_chat),
        ("思维链", example_thinking_chain),
        ("底层API", example_session_api),
        ("自定义ID", example_custom_device_id),
    ]

    print("可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n输入示例编号运行（输入 'all' 运行全部，输入 'q' 退出）")

    while True:
        choice = input("\n选择: ").strip().lower()

        if choice == "q":
            print("退出示例程序")
            break
        elif choice == "all":
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"示例 '{name}' 出错: {e}")
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    name, func = examples[idx]
                    func()
                else:
                    print("无效编号")
            except ValueError:
                print("请输入有效编号")


if __name__ == "__main__":
    main()