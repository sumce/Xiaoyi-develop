---
name: xiaoyi-query
description: 使用 Xiaoyi SDK 向华为小艺AI客服查询鸿蒙开发相关问题
version: 1.0.0
author: sumce
tags: [harmonyos, query, tool, reverse-api]
---

# XiaoYi Query Skill - 鸿蒙开发问题查询工具

## ⚠️ 重要声明

**本 Skill 基于逆向工程实现，仅供学习和研究使用！**

- **严禁商业用途**
- **严禁恶意滥用**
- **仅供技术研究**

使用前必须阅读：[免责声明](DISCLAIMER.md)

---

## Purpose

**让 AI 学会使用 Xiaoyi SDK 工具查询鸿蒙开发相关问题。**

当用户询问鸿蒙开发、DevEco Studio、ArkTS 等问题时，AI 应调用本 Skill 提供的工具向华为小艺AI客服查询，获取准确的官方技术解答。

---

## When to Use

### 适用场景

**应该使用本 Skill 的情况：**

- ✅ 用户询问鸿蒙开发技术问题
- ✅ 用户询问 DevEco Studio 使用问题
- ✅ 用户询问 ArkTS 语言问题
- ✅ 用户询问鸿蒙应用架构问题
- ✅ 用户询问鸿蒙生态和前景问题
- ✅ 需要华为官方客服的技术解答

**不应该使用的情况：**

- ❌ 用户询问其他非鸿蒙问题
- ❌ 用户需要代码编写帮助（应该由 AI 直接提供）
- ❌ 用户需要项目开发指导
- ❌ 查询敏感、政治、宗教等非技术内容

---

## How to Use

### 1. 调用核心脚本

```bash
python scripts/query_xiaoyi.py "你的问题"
```

### 2. 基本查询示例

```python
# 使用 Xiaoyi SDK 查询
from xiaoyi_sdk import XiaoyiAI, SSEMessage, IncrementalTracker

# 创建客户端
ai = XiaoyiAI()

# 流式查询
tracker = IncrementalTracker()
for chunk in ai.chat("鸿蒙开发需要什么基础？"):
    msg = SSEMessage(chunk)
    if msg.has_text:
        delta = tracker.new_text(msg)
        print(delta, end="", flush=True)
```

---

## Workflow

### AI 使用本 Skill 的标准流程

```
1. 用户问题识别
   ↓
   "用户询问鸿蒙开发问题"

2. AI 读取 Skill
   ↓
   读取 SKILL.md 规则和 Prompt

3. 构造查询
   ↓
   使用 prompts/query.md 模板构造问题

4. 执行查询
   ↓
   调用 scripts/query_xiaoyi.py

5. SDK 调用
   ↓
   Xiaoyi SDK → 华为小艺AI客服

6. 流式响应
   ↓
   SSE 消息 → IncrementalTracker 解析

7. 返回结果
   ↓
   格式化输出 → AI → 用户
```

---

## Prompt Templates

### 标准查询 Prompt

使用 `prompts/query.md` 提供的标准模板：

```
我有一个鸿蒙开发问题：
[用户问题]

请提供：
1. 技术解答
2. 相关文档链接（如有）
3. 最佳实践建议
```

### 查询类型分类

参考 `prompts/query.md` 中的分类：

| 类型 | 示例问题 |
|------|---------|
| **基础入门** | "鸿蒙开发需要什么基础？" |
| **开发工具** | "DevEco Studio 如何配置？" |
| **语言学习** | "ArkTS 和 TypeScript 有什么区别？" |
| **应用架构** | "鸿蒙应用如何设计架构？" |
| **生态前景** | "鸿蒙开发的就业前景如何？" |

---

## Tool Integration

### 核心：scripts/query_xiaoyi.py

**这是 AI 调用的核心工具脚本。**

功能：
- 集成 Xiaoyi SDK
- 流式查询华为小艺AI
- 处理 SSE 响应
- 提取增量文本
- 格式化输出

使用：
```bash
# 基本查询
python scripts/query_xiaoyi.py "鸿蒙开发前景如何"

# 深度思考模式
python scripts/query_xiaoyi.py "DevEco Studio 详细配置" --deep

# 显示思维链
python scripts/query_xiaoyi.py "ArkTS 性能优化" --thinking
```

---

## Response Format

### 标准响应格式

使用 `templates/response_template.md`：

```
## 📝 华为小艺AI回答

**问题**: [用户问题]

**回答**:
[小艺AI的完整回答]

**参考文档**（如有）:
- [文档链接]

**思维链**（可选）:
[AI推理过程]

---
查询时间: [时间]
设备ID: [anonymousId]
对话ID: [dialogId]
```

---

## Examples

### 实际使用示例

参考 `examples/` 目录：

1. **[examples/basic_query.py](examples/basic_query.py)** - 基础查询
2. **[examples/multi_turn.py](examples/multi_turn.py)** - 多轮对话
3. **[examples/thinking_chain.py](examples/thinking_chain.py)** - 思维链显示

---

## Constraints

### 使用限制

**必须遵守的限制：**

1. **额度限制**
   - 每个 anonymousId 有试用额度
   - 额度用完需生成新 ID
   - 建议适度使用

2. **频率限制**
   - 遵守 API 速率限制
   - 避免高频请求
   - 失败最多重试 3 次

3. **内容限制**
   - 仅查询技术问题
   - 不查询敏感内容
   - 不传播不当言论

4. **法律限制**
   - 仅供学习研究
   - 严禁商业用途
   - 遵守相关法规

---

## Error Handling

### 常见错误及处理

| 错误 | 原因 | AI 处理方式 |
|------|------|------------|
| QuotaExceededError | 额度用完 | 提示用户稍后再试或更换 ID |
| NetworkError | 网络问题 | 提示检查网络连接 |
| DialogError | 对话无效 | 自动重置对话 |
| TimeoutError | 超时 | 建议简化问题或稍后重试 |

---

## Best Practices

### AI 使用最佳实践

1. **问题构造**
   - 清晰、具体、技术性强
   - 避免模糊或过于宽泛
   - 提供必要上下文

2. **响应处理**
   - 流式处理提高体验
   - 正确解析 SSE 消息
   - 提取纯增量文本

3. **多轮对话**
   - 保持上下文连续性
   - 自动使用 subType=1
   - 避免频繁重置

4. **用户体验**
   - 提供清晰的查询结果
   - 格式化输出便于阅读
   - 附加参考文档链接

---

## Safety & Legal

### 法律和安全声明

**必须向用户说明：**

- 本工具基于逆向工程，仅供学习研究
- 非华为官方接口
- 请遵守华为开发者联盟使用条款
- 不得用于商业或非法用途

**详细声明见：[DISCLAIMER.md](DISCLAIMER.md) 和 [docs/LEGAL.md](docs/LEGAL.md)**

---

## Quick Reference

### AI 快速参考卡片

```
目的: 查询鸿蒙开发问题
工具: scripts/query_xiaoyi.py
SDK: XiaoyiAI.chat()
格式: templates/response_template.md

何时使用:
  ✅ 鸿蒙开发问题
  ✅ DevEco Studio 问题
  ✅ ArkTS 语言问题

如何调用:
  python scripts/query_xiaoyi.py "问题"

响应格式:
  ## 华为小艺AI回答
  [完整回答]

限制:
  - 仅技术问题
  - 有额度限制
  - 仅供学习研究
```

---

## Resources

### 相关资源

- **Prompt 模板**: [prompts/query.md](prompts/query.md)
- **核心脚本**: [scripts/query_xiaoyi.py](scripts/query_xiaoyi.py)
- **响应模板**: [templates/response_template.md](templates/response_template.md)
- **使用示例**: [examples/](examples/)
- **免责声明**: [DISCLAIMER.md](DISCLAIMER.md)
- **法律声明**: [docs/LEGAL.md](docs/LEGAL.md)
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)

---

## Changelog

- **v1.0.0** (2026-06-28): 初始版本，集成基础查询功能

---

## License

**仅供学习和研究使用，严禁商业用途。**

详见 [DISCLAIMER.md](DISCLAIMER.md)。