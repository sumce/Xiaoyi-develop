#!/usr/bin/env python3
"""交互式命令行聊天程序

提供一个简单的命令行聊天界面，支持：
- 多轮对话
- 显示思维链
- 实时流式输出
- 新对话切换
"""

import sys
from pathlib import Path

# 添加 src 目录到路径（用于开发测试）
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xiaoyi_sdk import (
    XiaoyiAI,
    SSEMessage,
    IncrementalTracker,
    QuotaExceededError,
    DialogError,
    SubmissionError,
    generate_anonymous_id,
)


class InteractiveChat:
    """交互式聊天客户端"""

    def __init__(self, anonymous_id: str = None):
        """初始化聊天客户端

        Args:
            anonymous_id: 设备ID（可选）
        """
        self.ai = XiaoyiAI(anonymous_id=anonymous_id)
        self.tracker = IncrementalTracker()
        self.show_thinking = False
        self.think_type = 1  # 默认开启深度思考

    def print_welcome(self):
        """打印欢迎信息"""
        print("\n" + "=" * 60)
        print("  华为智能客服 - 交互式聊天")
        print("=" * 60)
        print(f"\n设备ID: {self.ai.anonymous_id[:16]}...")
        print("\n命令:")
        print("  /new     - 开始新对话")
        print("  /think   - 开启/关闭思维链显示")
        print("  /fast    - 切换到快速模式（关闭深度思考）")
        print("  /deep    - 切换到深度思考模式")
        print("  /id      - 显示当前设备ID和对话ID")
        print("  /help    - 显示帮助")
        print("  /quit    - 退出程序")
        print("\n提示: 直接输入问题即可开始对话")
        print("-" * 60)

    def process_response(self, query: str):
        """处理响应并显示

        Args:
            query: 用户问题
        """
        print(f"\n你: {query}")
        print("AI: ", end="", flush=True)

        self.tracker.reset()

        # 思维链缓冲
        thinking_buffer = ""

        try:
            for chunk in self.ai.chat(query, think_type=self.think_type):
                msg = SSEMessage(chunk)

                # 检查错误
                if msg.is_error:
                    print(f"\n[错误] {msg.error_message}")
                    return

                # 处理思维链
                if self.show_thinking and msg.has_thinking:
                    delta = self.tracker.new_thinking(msg)
                    if delta:
                        thinking_buffer += delta

                # 处理回答文本
                if msg.has_text:
                    delta = self.tracker.new_text(msg)
                    if delta:
                        print(delta, end="", flush=True)

                # 对话结束
                if msg.is_final:
                    print()

                    # 显示思维链（如果有）
                    if self.show_thinking and thinking_buffer:
                        print("\n--- 思维链 ---")
                        print(thinking_buffer[:300])
                        if len(thinking_buffer) > 300:
                            print("...（已截断）")
                        print("---")

                    print(f"\n[对话轮次: {self.ai.round_number}]")
                    return

        except QuotaExceededError as e:
            print(f"\n[额度已用完] {e}")
            print("提示: 输入 '/new' 生成新设备ID继续使用")
        except SubmissionError as e:
            print(f"\n[提交错误] {e}")
        except DialogError as e:
            print(f"\n[对话错误] {e}")
        except Exception as e:
            print(f"\n[未知错误] {e}")

    def handle_command(self, cmd: str) -> bool:
        """处理命令

        Args:
            cmd: 命令字符串

        Returns:
            是否继续运行
        """
        cmd = cmd.lower().strip()

        if cmd == "/quit" or cmd == "/exit":
            print("\n感谢使用，再见！")
            self.ai.close()
            return False

        elif cmd == "/new":
            self.ai.reset()
            new_id = generate_anonymous_id()
            self.ai = XiaoyiAI(anonymous_id=new_id)
            print(f"\n已开始新对话")
            print(f"新设备ID: {self.ai.anonymous_id[:16]}...")

        elif cmd == "/think":
            self.show_thinking = not self.show_thinking
            status = "开启" if self.show_thinking else "关闭"
            print(f"\n思维链显示: {status}")

        elif cmd == "/fast":
            self.think_type = 0
            print("\n已切换到快速模式（关闭深度思考）")

        elif cmd == "/deep":
            self.think_type = 1
            print("\n已切换到深度思考模式")

        elif cmd == "/id":
            print(f"\n设备ID: {self.ai.anonymous_id}")
            print(f"对话ID: {self.ai.dialog_id or '未创建'}")
            print(f"轮次: {self.ai.round_number}")

        elif cmd == "/help":
            self.print_welcome()

        elif cmd == "/status":
            print(f"\n当前状态:")
            print(f"  深度思考: {'开启' if self.think_type == 1 else '关闭'}")
            print(f"  思维链显示: {'开启' if self.show_thinking else '关闭'}")
            print(f"  对话轮次: {self.ai.round_number}")

        else:
            print(f"\n未知命令: {cmd}")
            print("输入 /help 查看可用命令")

        return True

    def run(self):
        """运行交互式聊天"""
        self.print_welcome()

        while True:
            try:
                user_input = input("\n输入问题或命令: ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                else:
                    # 处理问题
                    self.process_response(user_input)

            except KeyboardInterrupt:
                print("\n\n检测到 Ctrl+C，输入 /quit 退出")
            except EOFError:
                print("\n\n退出程序")
                self.ai.close()
                break


def main():
    """主函数"""
    print("\n正在启动交互式聊天程序...")

    # 可选择自定义设备ID
    import argparse

    parser = argparse.ArgumentParser(description="交互式聊天程序")
    parser.add_argument(
        "--id",
        type=str,
        help="自定义设备ID（可选）",
    )
    parser.add_argument(
        "--think",
        action="store_true",
        help="默认显示思维链",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="使用快速模式（关闭深度思考）",
    )

    args = parser.parse_args()

    # 创建聊天客户端
    chat = InteractiveChat(anonymous_id=args.id)

    if args.think:
        chat.show_thinking = True

    if args.fast:
        chat.think_type = 0

    # 运行
    try:
        chat.run()
    except Exception as e:
        print(f"\n程序异常: {e}")
        chat.ai.close()


if __name__ == "__main__":
    main()