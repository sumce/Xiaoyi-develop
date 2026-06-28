#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaoYi Query Tool - 鸿蒙开发问题查询工具（直接从旧项目提取）

直接调用华为开发者联盟智能客服 API，无需 SDK
核心代码直接从旧项目 session.py 提取，确保 API 调用正确

作者: sumce
版本: 2.0.2（UTF-8 修复版）
"""

import argparse
import hashlib
import json
import sys
import uuid
from typing import Optional, Generator
import requests

# 强制设置 UTF-8 输出（修复 Windows PowerShell 乱码问题）
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')


# ==================== 配置常量（从旧项目提取）====================

API_BASE = "https://svc-drcn.developer.huawei.com/intelligentcustomer/v1/public"
URL_DIALOG_ID = f"{API_BASE}/dialog/id"
URL_SUBMISSION = f"{API_BASE}/dialog/submission"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    "Origin": "https://developer.huawei.com",
    "Referer": "https://developer.huawei.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


# ==================== 工具函数 ====================

def generate_anonymous_id() -> str:
    """
    生成设备指纹 ID（MD5）

    Returns:
        32位 MD5 设备指纹
    """
    random_uuid = str(uuid.uuid4())
    md5_hash = hashlib.md5(random_uuid.encode()).hexdigest()
    return md5_hash


# ==================== 核心类（直接从旧项目提取）====================

class XiaoYiQuery:
    """华为小艺AI查询客户端（直接从旧项目提取，确保正确）"""

    def __init__(self, anonymous_id: Optional[str] = None):
        """初始化查询客户端"""
        self.anonymous_id = anonymous_id or generate_anonymous_id()
        self.dialog_id: Optional[str] = None
        self._http = requests.Session()
        self._http.headers.update(HEADERS)

    def create_dialog(self, type_: int = 1001) -> str:
        """
        POST /dialog/id → 获取 dialogId

        Args:
            type_: 对话类型 (1001=知识问答)

        Returns:
            dialogId (UUID 字符串)

        Raises:
            Exception: 创建失败
        """
        body = {
            "origin": 0,
            "type": type_,
            "anonymousId": self.anonymous_id,
        }
        resp = self._http.post(
            URL_DIALOG_ID,
            json=body,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            timeout=15,
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"[{data.get('code')}] {data.get('message', 'unknown')}")

        self.dialog_id = data["result"]["dialogId"]
        return self.dialog_id

    def ask(
        self,
        query: str,
        *,
        stream: bool = True,
        type_: int = 1001,
        sub_type: int = 2,
        think_type: int = 1,
    ) -> Generator[str, None, None] | str:
        """
        POST /dialog/submission → 提交问题

        Args:
            query:   问题文本
            stream:  是否 SSE 流式返回
            type_:   对话类型
            sub_type: 2=新对话第一轮, 1=跟进
            think_type: 1=深度思考, 0=关闭

        Yields (stream=True): 流式回答文本
        Returns (stream=False): 完整回答文本

        Raises:
            Exception: API 返回错误
        """
        if not self.dialog_id:
            raise Exception("请先调用 create_dialog()")

        body = {
            "type": type_,
            "query": query,
            "dialogId": self.dialog_id,
            "channel": 1,
            "origin": 0,
            "subType": sub_type,
            "thinkType": think_type,
            "anonymousId": self.anonymous_id,
        }

        resp = self._http.post(
            URL_SUBMISSION,
            json=body,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            stream=stream,
            timeout=120,
        )

        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")

        # 解析 SSE 流式响应
        if stream:
            accumulated_text = ""
            accumulated_thinking = ""

            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue

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
                        yield f"\033[90m{new_thinking}\033[0m"

                    # 提取回答文本
                    text = result.get("streamingText", "")
                    if text and len(text) > len(accumulated_text):
                        new_text = text[len(accumulated_text):]
                        accumulated_text = text
                        yield new_text

                    # 检查是否结束
                    if result.get("isFinal"):
                        break

                except json.JSONDecodeError:
                    continue

        else:
            # 非流式模式
            full_text = ""
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                json_str = line[5:].strip()
                if not json_str:
                    continue
                try:
                    chunk = json.loads(json_str)
                    if chunk.get("code") == 0:
                        result = chunk.get("result", {})
                        text = result.get("streamingText", "")
                        if text:
                            full_text = text
                        if result.get("isFinal"):
                            break
                except json.JSONDecodeError:
                    continue
            return full_text

    def close(self):
        """关闭会话"""
        self._http.close()


# ==================== 主函数 ====================

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
    print("║     XiaoYi Query Tool v2.0.2         ║")
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