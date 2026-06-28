#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaoYi Query Tool - 鸿蒙开发问题查询工具（简化独立版）

直接调用华为开发者联盟智能客服 API，无需 SDK
支持流式响应和思维链显示

作者: sumce
版本: 2.0.0（简化独立版）
"""

import argparse
import hashlib
import json
import sys
import time
import uuid
from typing import Optional, Generator
import requests


class XiaoYiQuery:
    """华为小艺AI查询客户端（独立版，无需 SDK）"""

    # 华为开发者联盟智能客服 API 端点
    API_BASE = "https://svc-drcn.developer.huawei.com/intelligentcustomer/v1/public"
    URL_DIALOG_ID = "/dialog/id"
    URL_SUBMISSION = "/dialog/submission"

    def __init__(self):
        """初始化查询客户端"""
        self.session = requests.Session()
        self.anonymous_id = self._generate_anonymous_id()
        self.dialog_id: Optional[str] = None
        self.dialog_created = False

        # 设置请求头
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://developer.huawei.com",
            "Referer": "https://developer.huawei.com/",
        }

    def _generate_anonymous_id(self) -> str:
        """
        生成设备指纹 ID（MD5）

        Returns:
            32位 MD5 设备指纹
        """
        # 生成随机 UUID
        random_uuid = str(uuid.uuid4())
        # 计算 MD5
        md5_hash = hashlib.md5(random_uuid.encode()).hexdigest()
        return md5_hash

    def create_dialog(self) -> str:
        """
        创建新对话

        Returns:
            对话 ID

        Raises:
            Exception: 创建对话失败
        """
        url = f"{self.API_BASE}{self.URL_DIALOG_ID}"

        data = {
            "anonymousId": self.anonymous_id,
            "dialogType": 1001,
            "channel": 1,
            "origin": 0,
        }

        try:
            response = self.session.post(
                url,
                headers=self.headers,
                json=data,
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f"HTTP错误: {response.status_code}")

            result = response.json()

            if result.get("code") != 0:
                raise Exception(f"API错误: {result.get('message', '未知错误')}")

            self.dialog_id = result.get("result", {}).get("dialogId")
            self.dialog_created = True

            return self.dialog_id

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络错误: {str(e)}")

    def ask(
        self,
        question: str,
        stream: bool = True,
        think_type: int = 1,
        sub_type: int = 2,
    ) -> Generator[str, None, None]:
        """
        提交问题并获取回答

        Args:
            question: 问题内容
            stream: 是否流式返回
            think_type: 思考类型（1=深度思考，0=快速）
            sub_type: 对话类型（2=首轮，1=跟进）

        Yields:
            流式回答文本片段

        Raises:
            Exception: 提交失败
        """
        # 如果对话未创建，先创建
        if not self.dialog_created:
            self.create_dialog()

        url = f"{self.API_BASE}{self.URL_SUBMISSION}"

        data = {
            "anonymousId": self.anonymous_id,
            "dialogId": self.dialog_id,
            "query": question,
            "subType": sub_type,
            "thinkType": think_type,
            "channel": 1,
            "origin": 0,
            "dialogType": 1001,
        }

        try:
            response = self.session.post(
                url,
                headers=self.headers,
                json=data,
                stream=True,
                timeout=120,
            )

            if response.status_code != 200:
                raise Exception(f"HTTP错误: {response.status_code}")

            # 解析 SSE 流式响应
            accumulated_text = ""
            accumulated_thinking = ""

            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue

                # 提取 JSON 数据
                json_str = line[5:].strip()
                if not json_str:
                    continue

                try:
                    chunk = json.loads(json_str)

                    # 检查错误
                    if chunk.get("code") != 0:
                        error_msg = chunk.get("message", "未知错误")
                        raise Exception(f"API错误: {error_msg}")

                    result = chunk.get("result", {})

                    # 提取思维链（如果有）
                    thinking = result.get("thinking", "")
                    if thinking and len(thinking) > len(accumulated_thinking):
                        new_thinking = thinking[len(accumulated_thinking):]
                        accumulated_thinking = thinking
                        if stream:
                            yield f"\033[90m{new_thinking}\033[0m"

                    # 提取回答文本
                    text = result.get("streamingText", "")
                    if text and len(text) > len(accumulated_text):
                        new_text = text[len(accumulated_text):]
                        accumulated_text = text
                        if stream:
                            yield new_text

                    # 检查是否结束
                    if result.get("isFinal"):
                        break

                except json.JSONDecodeError:
                    continue

            # 返回完整文本（非流式模式）
            if not stream:
                yield accumulated_text

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络错误: {str(e)}")

    def reset(self):
        """重置对话，开始新对话"""
        self.dialog_id = None
        self.dialog_created = False

    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XiaoYi Query Tool - 鸿蒙开发问题查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python query_xiaoyi.py "什么是鸿蒙开发"
  python query_xiaoyi.py "ArkUI 如何使用" --thinking
  python query_xiaoyi.py "如何配置 DevEco Studio" --deep
        """,
    )

    parser.add_argument("question", help="要查询的问题")
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="显示 AI 思维链（深度思考模式）",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="深度分析模式",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="非流式输出（等待完整响应）",
    )

    args = parser.parse_args()

    # 打印工具信息
    print("\n")
    print("╔═══════════════════════════════════════╗")
    print("║     XiaoYi Query Tool v2.0.0         ║")
    print("║     鸿蒙开发智能查询助手               ║")
    print("║     （独立版 - 无需 SDK）             ║")
    print("╚═══════════════════════════════════════╝")
    print()

    print(f"📝 问题: {args.question}")
    print(f"🔄 模式: {'深度思考' if args.thinking else '快速查询'}")
    print()

    # 创建查询客户端
    client = XiaoYiQuery()

    try:
        # 创建对话
        print("⏳ 正在连接华为小艺 AI...")
        dialog_id = client.create_dialog()
        print(f"✅ 对话创建成功 (ID: {dialog_id[:16]}...)")
        print()

        # 设置思考类型
        think_type = 1 if args.thinking or args.deep else 0

        # 查询问题
        print("🤖 小艺回答:")
        print("─" * 50)

        full_response = ""
        for chunk in client.ask(
            args.question,
            stream=not args.no_stream,
            think_type=think_type,
        ):
            print(chunk, end="", flush=True)
            full_response += chunk.replace("\033[90m", "").replace("\033[0m", "")

        print()
        print("─" * 50)
        print()

        # 显示对话 ID（可用于继续对话）
        print(f"💡 对话 ID: {dialog_id}")
        print(f"💡 设备 ID: {client.anonymous_id}")
        print()

        # 显示免责声明
        print("⚠️  免责声明:")
        print("   - 本工具基于逆向工程，非华为官方接口")
        print("   - 仅供学习研究使用，严禁商业用途")
        print("   - 使用风险自负，请遵守华为开发者服务条款")
        print()

        # 关闭会话
        client.close()

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print()
        print("🔍 可能的原因:")
        print("   1. 网络连接问题")
        print("   2. 华为 API 端点已变更")
        print("   3. 试用额度已用完")
        print()
        print("💡 建议:")
        print("   - 检查网络连接")
        print("   - 查看 GitHub 项目更新: https://github.com/sumce/Xiaoyi-develop")
        print("   - 生成新的设备 ID 重试")
        print()

        client.close()
        sys.exit(1)


if __name__ == "__main__":
    main()