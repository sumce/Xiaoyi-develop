#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话示例

演示如何使用 XiaoYi Query Tool 进行多轮对话式查询

作者: XiaoYi Skill
"""

import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query_xiaoyi import XiaoYiQuery


class MultiTurnConversation:
    """多轮对话管理器"""
    
    def __init__(self):
        self.client = XiaoYiQuery()
        self.conversation_history = []
    
    def add_to_history(self, question: str, answer: str):
        """
        添加对话到历史
        
        Args:
            question: 用户问题
            answer: AI回答
        """
        self.conversation_history.append({
            "question": question,
            "answer": answer
        })
    
    def build_contextual_question(self, new_question: str) -> str:
        """
        构建带上下文的问题
        
        Args:
            new_question: 新问题
        
        Returns:
            包含历史上下文的问题
        """
        if not self.conversation_history:
            return new_question
        
        # 构建上下文
        context = "之前的对话内容：\n"
        for i, turn in enumerate(self.conversation_history[-2:], 1):  # 只保留最近2轮
            context += f"\n第{i}轮：\n"
            context += f"问：{turn['question']}\n"
            context += f"答：{turn['answer'][:200]}...\n"  # 只保留回答的前200字符
        
        context += f"\n当前问题：{new_question}"
        return context
    
    def ask(self, question: str, use_context: bool = True) -> str:
        """
        提问
        
        Args:
            question: 问题内容
            use_context: 是否使用历史上下文
        
        Returns:
            AI回答
        """
        if use_context and self.conversation_history:
            contextual_question = self.build_contextual_question(question)
        else:
            contextual_question = question
        
        print(f"\n【用户】{question}")
        print("\n【小艺】")
        
        try:
            # 使用流式输出
            answer = self.client.query(contextual_question, mode="normal", stream=True)
            
            # 添加到历史
            self.add_to_history(question, answer)
            
            return answer
            
        except Exception as e:
            print(f"错误: {str(e)}")
            return ""
    
    def show_history(self):
        """显示对话历史"""
        print("\n" + "=" * 60)
        print("对话历史")
        print("=" * 60)
        
        for i, turn in enumerate(self.conversation_history, 1):
            print(f"\n第{i}轮对话：")
            print(f"问：{turn['question']}")
            print(f"答：{turn['answer'][:100]}...")


def example_sequential_questions():
    """顺序问答示例"""
    print("=" * 60)
    print("示例 1: 顺序问答 - 鸿蒙组件开发")
    print("=" * 60)
    
    conversation = MultiTurnConversation()
    
    # 第一轮：基础概念
    conversation.ask("什么是鸿蒙的 @Component 组件？")
    
    # 第二轮：深入理解（基于前一轮的上下文）
    conversation.ask("如何在这个组件中使用状态管理？")
    
    # 第三轮：具体实现
    conversation.ask("可以提供一个完整的登录组件示例吗？")
    
    # 显示对话历史
    conversation.show_history()


def example_topic_deepening():
    """主题深入示例"""
    print("\n\n" + "=" * 60)
    print("示例 2: 主题深入 - 性能优化")
    print("=" * 60)
    
    conversation = MultiTurnConversation()
    
    # 从基础到深入的问题序列
    questions = [
        "鸿蒙应用性能优化的基本原则是什么？",
        "LazyForEach 和 ForEach 的性能差异有多大？",
        "如何正确实现 LazyForEach 的数据源接口？",
        "优化大型列表时，还有哪些需要注意的点？"
    ]
    
    for question in questions:
        conversation.ask(question)
        print("\n" + "-" * 60)


def example_problem_solving():
    """问题解决流程示例"""
    print("\n\n" + "=" * 60)
    print("示例 3: 问题解决流程")
    print("=" * 60)
    
    conversation = MultiTurnConversation()
    
    # 模拟实际问题解决流程
    print("\n场景：开发者遇到页面跳转失败的问题\n")
    
    # 问题1：描述问题
    conversation.ask(
        "我的鸿蒙应用使用 router.push() 进行页面跳转，但是跳转失败了，可能是什么原因？"
    )
    
    # 问题2：基于回答追问
    conversation.ask(
        "检查了路由配置，看起来没问题。还有其他可能的原因吗？"
    )
    
    # 问题3：寻求具体解决方案
    conversation.ask(
        "如果是因为目标页面还没加载，有什么办法可以确保页面跳转成功？"
    )
    
    # 问题4：代码示例
    conversation.ask(
        "可以提供一个带错误处理的页面跳转代码示例吗？"
    )


def example_without_context():
    """不使用上下文的示例"""
    print("\n\n" + "=" * 60)
    print("示例 4: 无上下文查询对比")
    print("=" * 60)
    
    conversation = MultiTurnConversation()
    
    # 第一次查询
    conversation.ask("什么是 ArkTS 的声明式 UI？", use_context=False)
    
    # 第二次查询 - 不使用上下文
    print("\n【对比】不使用历史上下文的查询：")
    conversation.ask("它有什么特点？", use_context=False)
    
    # 第三次查询 - 使用上下文
    print("\n【对比】使用历史上下文的查询：")
    conversation.ask("它有什么特点？", use_context=True)


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════╗
║   XiaoYi Query Tool - 多轮对话示例     ║
╚════════════════════════════════════════╝

多轮对话可以：
1. 保持对话上下文，使回答更连贯
2. 深入探讨特定主题
3. 逐步解决问题

    """)
    
    try:
        # 运行示例
        example_sequential_questions()
        example_topic_deepening()
        example_problem_solving()
        example_without_context()
        
        print("\n\n" + "=" * 60)
        print("示例完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        sys.exit(0)


if __name__ == "__main__":
    main()