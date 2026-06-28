#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思维链显示示例

演示如何使用 XiaoYi Query Tool 的思维链模式 (--thinking)

作者: XiaoYi Skill
"""

import sys
import os
import time

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_xiaoyi import XiaoYiQuery


def print_thinking_header(question: str):
    """打印思维链头部"""
    print("=" * 70)
    print("🤔 思维链分析模式")
    print("=" * 70)
    print(f"\n问题：{question}\n")
    print("=" * 70)
    print("\n开始逐步思考...\n")


def print_thinking_step(step_number: int, title: str):
    """打印思考步骤标题"""
    print(f"\n{'▶' * 5} 步骤 {step_number}: {title} {'▶' * 5}\n")


def example_architecture_decision():
    """架构决策思维链示例"""
    print("=" * 70)
    print("示例 1: 架构决策 - MVVM vs Clean Architecture")
    print("=" * 70)
    
    client = XiaoYiQuery()
    
    question = """
需要为一个新的鸿蒙应用项目选择架构：
- 项目规模：中等（10-15个页面）
- 团队：4人，其中2人刚接触鸿蒙
- 需求：未来可能扩展到多个平台

请对比 MVVM 和 Clean Architecture，并给出选择建议。
"""
    
    print_thinking_header(question)
    
    try:
        # 使用思维链模式，非流式以展示完整结构
        response = client.query(question, mode="thinking", stream=False)
        
        # 格式化输出思维链
        print("\n【思维链过程】\n")
        print(response)
        
        # 提取关键结论
        print("\n" + "=" * 70)
        print("📌 关键结论")
        print("=" * 70)
        
    except Exception as e:
        print(f"错误: {str(e)}")


def example_technology_selection():
    """技术选型思维链示例"""
    print("\n\n" + "=" * 70)
    print("示例 2: 技术选型 - 数据存储方案")
    print("=" * 70)
    
    client = XiaoYiQuery()
    
    question = """
鸿蒙应用需要持久化存储用户数据：
- 数据类型：用户配置、离线数据、缓存
- 数据量：预计最大100MB
- 性能要求：读写频繁，需要快速响应

可选方案：
1. LocalStorage（本地存储）
2. Preferences（偏好设置）
3. RdbStore（关系型数据库）
4. 分布式数据服务

请分析并推荐最适合的方案组合。
"""
    
    print_thinking_header(question)
    
    try:
        response = client.query(question, mode="thinking", stream=False)
        print("\n【思维链过程】\n")
        print(response)
        
    except Exception as e:
        print(f"错误: {str(e)}")


def example_performance_optimization():
    """性能优化思维链示例"""
    print("\n\n" + "=" * 70)
    print("示例 3: 性能优化 - 列表渲染问题")
    print("=" * 70)
    
    client = XiaoYiQuery()
    
    question = """
遇到一个大型列表性能问题：
- 数据：1000+ 条记录，每条包含图片和文本
- 问题：滚动卡顿，内存占用高
- 已尝试：使用 LazyForEach，但效果不明显

请系统分析问题原因和优化步骤。
"""
    
    print_thinking_header(question)
    
    try:
        # 使用流式输出，展示实时思考过程
        print("\n【实时思考过程】\n")
        response = client.query(question, mode="thinking", stream=True)
        
    except Exception as e:
        print(f"错误: {str(e)}")


def example_debugging_analysis():
    """调试分析思维链示例"""
    print("\n\n" + "=" * 70)
    print("示例 4: 调试分析 - 运行时错误")
    print("=" * 70)
    
    client = XiaoYiQuery()
    
    question = """
应用运行时遇到错误：
- 错误信息："Component build() called multiple times"
- 场景：页面跳转后返回时出现
- 代码：在 build() 方法中使用了 @State 变量

请分析错误原因和解决方法。
"""
    
    print_thinking_header(question)
    
    # 模拟分步思考展示
    steps = [
        "理解错误信息含义",
        "识别可能的触发条件",
        "分析代码逻辑",
        "推导根本原因",
        "制定解决方案"
    ]
    
    print("\n【逐步思考】\n")
    
    try:
        for i, step in enumerate(steps, 1):
            print_thinking_step(i, step)
            time.sleep(0.3)  # 模拟思考延迟
        
        print("\n【完整分析】\n")
        response = client.query(question, mode="thinking", stream=False)
        print(response)
        
    except Exception as e:
        print(f"错误: {str(e)}")


def example_comparison_mode():
    """对比模式：思维链 vs 深度查询"""
    print("\n\n" + "=" * 70)
    print("示例 5: 模式对比 - 思维链 vs 深度查询")
    print("=" * 70)
    
    client = XiaoYiQuery()
    
    question = "如何设计一个可扩展的鸿蒙应用架构？"
    
    print(f"\n问题：{question}\n")
    print("=" * 70)
    
    # 深度查询
    print("\n【深度查询模式】\n")
    print("重点：提供详细解决方案和最佳实践")
    print("-" * 70)
    try:
        response_deep = client.query(question, mode="deep", stream=False)
        print(response_deep[:500] + "...\n")  # 显示部分内容
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 思维链
    print("\n【思维链模式】\n")
    print("重点：展示推理过程和决策依据")
    print("-" * 70)
    try:
        response_thinking = client.query(question, mode="thinking", stream=False)
        print(response_thinking[:500] + "...\n")  # 显示部分内容
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("\n" + "=" * 70)
    print("💡 模式区别：")
    print("   - 深度查询：详细的技术方案和实践建议")
    print("   - 思维链：完整的推理过程和决策依据")
    print("=" * 70)


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════╗
║  XiaoYi Query Tool - 思维链显示示例        ║
╚════════════════════════════════════════════╝

思维链模式 (--thinking) 特点：
1. 展示完整的推理过程
2. 分步分析问题
3. 对比多个方案
4. 提供决策依据
5. 适合复杂决策和学习理解

适用场景：
- 架构设计决策
- 技术方案对比
- 问题诊断分析
- 学习技术原理

    """)
    
    try:
        # 运行示例
        example_architecture_decision()
        example_technology_selection()
        example_performance_optimization()
        example_debugging_analysis()
        example_comparison_mode()
        
        print("\n\n" + "=" * 70)
        print("✅ 示例完成")
        print("=" * 70)
        print("\n💡 使用建议：")
        print("   - 复杂决策使用 --thinking 模式")
        print("   - 技术问题使用 --deep 模式")
        print("   - 快速问答使用普通模式")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(0)


if __name__ == "__main__":
    main()