#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaoYi Query Tool - 鸿蒙开发问题查询工具

使用华为小艺AI进行鸿蒙开发相关的智能查询
支持普通查询、深度查询和思维链模式

作者: XiaoYi Skill
版本: 1.0.0
"""

import argparse
import json
import sys
import time
from typing import Optional, Dict, Any, Generator
import requests


class XiaoYiQuery:
    """华为小艺AI查询客户端"""
    
    def __init__(self, endpoint: str = "https://xiaoyi.huawei.com/api/v1/query"):
        """
        初始化查询客户端
        
        Args:
            endpoint: 小艺AI服务端点
        """
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "XiaoYi-Query-Tool/1.0"
        }
    
    def build_prompt(self, question: str, mode: str = "normal") -> str:
        """
        根据查询模式构建Prompt
        
        Args:
            question: 用户问题
            mode: 查询模式 (normal/deep/thinking)
        
        Returns:
            构建后的Prompt字符串
        """
        if mode == "deep":
            prompt = f"""你是一位资深的鸿蒙开发专家，请深入分析以下问题：

{question}

请提供：
1. 问题背景分析
2. 核心技术原理说明
3. 详细的解决方案
4. 最佳实践建议
5. 相关参考资料

请确保回答详细、专业、具有指导性。"""
        elif mode == "thinking":
            prompt = f"""你是一位资深的鸿蒙开发专家，请使用思维链方式分析以下问题：

{question}

请详细展示你的推理过程，包括：
1. 问题理解与分解
2. 关键因素识别
3. 可能方案对比
4. 最优方案推导
5. 实施建议

请逐步思考，展示完整的分析过程。"""
        else:
            prompt = f"""你是一位鸿蒙开发专家，请回答以下问题：

{question}

请提供清晰、准确、实用的回答。"""
        
        return prompt
    
    def parse_sse_message(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析SSE消息
        
        Args:
            line: SSE消息行
        
        Returns:
            解析后的字典，如果无效则返回None
        """
        if not line or not line.startswith("data:"):
            return None
        
        try:
            data_str = line[5:].strip()  # 移除 "data:" 前缀
            if not data_str:
                return None
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None
    
    def extract_text(self, data: Dict[str, Any]) -> str:
        """
        从响应数据中提取文本
        
        Args:
            data: 响应数据字典
        
        Returns:
            提取的文本内容
        """
        # 适配不同的响应格式
        if "text" in data:
            return data["text"]
        elif "content" in data:
            return data["content"]
        elif "delta" in data and "content" in data["delta"]:
            return data["delta"]["content"]
        elif "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"]
            elif "text" in choice:
                return choice["text"]
        return ""
    
    def query_stream(self, question: str, mode: str = "normal") -> Generator[str, None, None]:
        """
        流式查询小艺AI
        
        Args:
            question: 用户问题
            mode: 查询模式
        
        Yields:
            增量文本片段
        """
        prompt = self.build_prompt(question, mode)
        
        payload = {
            "prompt": prompt,
            "mode": mode,
            "stream": True,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                data = self.parse_sse_message(line_str)
                
                if data:
                    text = self.extract_text(data)
                    if text:
                        yield text
                    
                    # 检查是否结束
                    if data.get("finish_reason") == "stop":
                        break
                        
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到小艺AI服务，请检查网络设置")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")
    
    def query(self, question: str, mode: str = "normal", stream: bool = True) -> str:
        """
        查询小艺AI
        
        Args:
            question: 用户问题
            mode: 查询模式
            stream: 是否使用流式输出
        
        Returns:
            完整的回答文本
        """
        if not stream:
            # 非流式模式，收集所有内容
            full_response = []
            for text in self.query_stream(question, mode):
                full_response.append(text)
            return "".join(full_response)
        else:
            # 流式模式，实时打印
            full_response = []
            for text in self.query_stream(question, mode):
                print(text, end='', flush=True)
                full_response.append(text)
            print()  # 结束换行
            return "".join(full_response)


def print_banner():
    """打印程序Banner"""
    banner = """
╔═══════════════════════════════════════╗
║     XiaoYi Query Tool v1.0.0         ║
║     鸿蒙开发智能查询助手               ║
╚═══════════════════════════════════════╝
    """
    print(banner)


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 50 + "\n")


def format_output(text: str, mode: str) -> str:
    """
    格式化输出文本
    
    Args:
        text: 原始文本
        mode: 查询模式
    
    Returns:
        格式化后的文本
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
查询时间: {timestamp}
查询模式: {mode}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    footer = """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
查询完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return header + text + footer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XiaoYi Query Tool - 鸿蒙开发智能查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 普通查询
  python query_xiaoyi.py "如何使用 TextInput 组件？"
  
  # 深度查询
  python query_xiaoyi.py --deep "详细分析 LazyForEach 性能优化方案"
  
  # 思维链模式
  python query_xiaoyi.py --thinking "对比 MVVM 和 Clean Architecture 在鸿蒙中的应用"
        """
    )
    
    parser.add_argument(
        "question",
        type=str,
        help="要查询的问题"
    )
    
    parser.add_argument(
        "--deep",
        action="store_true",
        help="使用深度查询模式，提供更详细的分析"
    )
    
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="使用思维链模式，展示推理过程"
    )
    
    parser.add_argument(
        "--endpoint",
        type=str,
        default="https://xiaoyi.huawei.com/api/v1/query",
        help="小艺AI服务端点 (默认: https://xiaoyi.huawei.com/api/v1/query)"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="禁用流式输出，等待完整响应后显示"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="XiaoYi Query Tool v1.0.0"
    )
    
    args = parser.parse_args()
    
    # 确定查询模式
    if args.deep:
        mode = "deep"
    elif args.thinking:
        mode = "thinking"
    else:
        mode = "normal"
    
    # 打印Banner
    print_banner()
    
    # 显示查询信息
    print(f"📝 问题: {args.question}")
    print(f"🔍 模式: {mode}")
    print_separator()
    
    try:
        # 创建查询客户端
        client = XiaoYiQuery(endpoint=args.endpoint)
        
        # 执行查询
        if args.no_stream:
            # 非流式模式
            print("⏳ 正在查询，请稍候...")
            response = client.query(
                args.question,
                mode=mode,
                stream=False
            )
            print(format_output(response, mode))
        else:
            # 流式模式
            print("💡 回答:\n")
            response = client.query(
                args.question,
                mode=mode,
                stream=True
            )
        
        print_separator()
        print("✅ 查询成功！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断查询")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}", file=sys.stderr)
        print("\n💡 建议:")
        print("  1. 检查网络连接")
        print("  2. 确认服务端点是否正确")
        print("  3. 尝试使用 --deep 或 --thinking 模式")
        print("  4. 查看错误日志获取详细信息")
        sys.exit(1)


if __name__ == "__main__":
    main()