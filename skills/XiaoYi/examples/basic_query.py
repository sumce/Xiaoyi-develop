#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础查询示例

演示如何使用 XiaoYi Query Tool 进行基础的鸿蒙开发问题查询

作者: XiaoYi Skill
"""

import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_xiaoyi import XiaoYiQuery


def example_basic_query():
    """基础查询示例"""
    print("=" * 60)
    print("示例 1: 基础查询")
    print("=" * 60)
    
    # 创建查询客户端
    client = XiaoYiQuery()
    
    # 示例问题列表
    questions = [
        "什么是 ArkTS？它与 TypeScript 有什么区别？",
        "如何在鸿蒙应用中使用 TextInput 组件？",
        "@State 和 @Prop 状态管理有什么不同？"
    ]
    
    # 逐个查询
    for i, question in enumerate(questions, 1):
        print(f"\n【问题 {i}】{question}\n")
        print("【回答】")
        try:
            # 使用流式输出
            response = client.query(question, mode="normal", stream=True)
            print("\n" + "-" * 60)
        except Exception as e:
            print(f"错误: {str(e)}")
            continue


def example_different_modes():
    """不同查询模式示例"""
    print("\n\n" + "=" * 60)
    print("示例 2: 不同查询模式对比")
    print("=" * 60)
    
    client = XiaoYiQuery()
    
    # 同一个问题，不同模式
    question = "鸿蒙应用如何进行性能优化？"
    
    print(f"\n【问题】{question}\n")
    
    # 普通模式
    print("\n【普通模式】")
    print("-" * 60)
    try:
        response = client.query(question, mode="normal", stream=True)
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 深度模式
    print("\n\n【深度模式】")
    print("-" * 60)
    try:
        response = client.query(question, mode="deep", stream=False)
        print(response)
    except Exception as e:
        print(f"错误: {str(e)}")


def example_specific_topic():
    """特定主题查询示例"""
    print("\n\n" + "=" * 60)
    print("示例 3: 特定主题查询 - 组件生命周期")
    print("=" * 60)
    
    client = XiaoYiQuery()
    
    # 构造详细的问题
    question = """请详细说明鸿蒙组件的生命周期：
1. aboutToAppear 和 aboutToDisappear 的调用时机
2. onPageShow 和 onPageHide 的区别
3. 如何在生命周期中管理资源
请提供代码示例。"""
    
    print(f"\n【问题】\n{question}\n")
    print("【回答】")
    try:
        response = client.query(question, mode="normal", stream=True)
    except Exception as e:
        print(f"错误: {str(e)}")


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════╗
║   XiaoYi Query Tool - 基础查询示例     ║
╚════════════════════════════════════════╝
    """)
    
    try:
        # 运行示例
        example_basic_query()
        example_different_modes()
        example_specific_topic()
        
        print("\n\n" + "=" * 60)
        print("示例完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        sys.exit(0)


if __name__ == "__main__":
    main()