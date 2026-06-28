# XiaoYi Query Skill - 鸿蒙开发问题查询工具

## ⚠️ 重要警告

**本 Skill 基于逆向工程实现，仅供学习和研究使用！**

- **非华为官方接口**
- **严禁商业用途**
- **严禁恶意滥用**
- **使用风险自负**

使用前必须阅读：[免责声明](DISCLAIMER.md)

---

## 📋 简介

**XiaoYi Query Skill** 是一个 Claude Code Skill，用于查询鸿蒙开发相关问题。

它集成了 Xiaoyi SDK，可以向华为小艺AI客服查询：
- 鸿蒙开发技术问题
- DevEco Studio 使用问题
- ArkTS 语言学习问题
- 鸿蒙应用架构问题
- 鸿蒙生态和前景问题

---

## 🎯 目的

**让 AI 学会使用这个工具查询鸿蒙开发问题。**

当用户询问鸿蒙开发问题时，AI 会：
1. 读取本 Skill 的规则和 Prompt
2. 调用 `scripts/query_xiaoyi.py` 执行查询
3. 使用 Xiaoyi SDK 向华为小艺AI客服提问
4. 处理 SSE 流式响应
5. 格式化输出结果给用户

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 已安装 Xiaoyi SDK（`pip install xiaoyi-sdk`）
- 网络连接正常

### 2. 使用方式

**命令行使用：**

```bash
# 基本查询
python scripts/query_xiaoyi.py "鸿蒙开发前景如何"

# 深度思考模式
python scripts/query_xiaoyi.py "DevEco Studio 详细配置" --deep

# 显示思维链
python scripts/query_xiaoyi.py "ArkTS 性能优化" --thinking
```

**Python 代码使用：**

```python
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

## 📚 Skill 结构

```
XiaoYi/
│
├── SKILL.md                 # Skill 入口（AI 读取）
├── README.md                # 本文档
├── DISCLAIMER.md            # 免责声明
│
├── prompts/                 # Prompt 模板
│   └── query.md             # 鸿蒙问题查询模板
│
├── scripts/                 # 核心工具脚本
│   └── query_xiaoyi.py      # 核心 SDK 集成脚本
│
├── templates/               # 输出模板
│   └── response_template.md # 响应格式模板
│
├── examples/                # 使用示例
│   ├── basic_query.py       # 基础查询
│   ├── multi_turn.py        # 多轮对话
│   └── thinking_chain.py    # 思维链显示
│
└── docs/                    # 文档（待创建）
    ├── LEGAL.md             # 法律声明
    ├── API.md               # API 文档
    └── FAQ.md               # 常见问题
```

---

## 🔧 核心功能

### 1. 核心脚本：query_xiaoyi.py

**这是 AI 调用的主要工具。**

功能：
- ✅ 集成 Xiaoyi SDK
- ✅ 流式查询华为小艺AI
- ✅ SSE 消息解析
- ✅ 增量文本提取
- ✅ 格式化输出
- ✅ 错误处理

### 2. 查询模式

| 模式 | 说明 | 命令 |
|------|------|------|
| **快速模式** | 快速获取答案 | 默认模式 |
| **深度思考** | 详细分析和推理 | `--deep` |
| **思维链** | 显示 AI 推理过程 | `--thinking` |

### 3. 多轮对话

支持自动保持上下文：
```python
ai = XiaoyiAI()

# 第一轮
ai.chat("鸿蒙开发前景如何？")

# 自动跟进（保持上下文）
ai.chat("那和Android比有什么优势？")
```

---

## 💡 使用示例

### 基础查询

参考：[examples/basic_query.py](examples/basic_query.py)

```python
from xiaoyi_sdk import XiaoyiAI, SSEMessage, IncrementalTracker

ai = XiaoyiAI()
tracker = IncrementalTracker()

for chunk in ai.chat("鸿蒙开发需要什么基础？"):
    msg = SSEMessage(chunk)
    if msg.has_text:
        delta = tracker.new_text(msg)
        print(delta, end="", flush=True)
```

### 多轮对话

参考：[examples/multi_turn.py](examples/multi_turn.py)

```python
ai = XiaoyiAI()

questions = [
    "鸿蒙开发需要什么基础？",
    "那和Java开发Android比有什么优势？",
    "DevEco Studio对硬件要求高吗？"
]

for q in questions:
    print(f"\n问题: {q}")
    print("回答: ", end="")
    tracker = IncrementalTracker()
    for chunk in ai.chat(q):
        msg = SSEMessage(chunk)
        if msg.has_text:
            delta = tracker.new_text(msg)
            print(delta, end="", flush=True)
    print()
```

### 思维链显示

参考：[examples/thinking_chain.py](examples/thinking_chain.py)

```python
ai = XiaoyiAI()
tracker = IncrementalTracker()

thinking_active = False
for chunk in ai.chat("ArkTS性能优化", think_type=1):
    msg = SSEMessage(chunk)
    
    # 显示思维链（灰色）
    if msg.has_thinking:
        delta = tracker.new_thinking(msg)
        if delta and not msg.has_text:
            print("\033[90m" + delta + "\033[0m", end="", flush=True)
    
    # 显示回答
    if msg.has_text:
        delta = tracker.new_text(msg)
        if delta:
            print(delta, end="", flush=True)
```

---

## 📖 Prompt 模板

参考：[prompts/query.md](prompts/query.md)

### 标准查询模板

```
我有一个鸿蒙开发问题：
[用户问题]

请提供：
1. 技术解答
2. 相关文档链接（如有）
3. 最佳实践建议
```

### 问题分类

| 类型 | 示例问题 |
|------|---------|
| **基础入门** | 鸿蒙开发需要什么基础？ |
| **开发工具** | DevEco Studio 如何配置？ |
| **语言学习** | ArkTS 和 TypeScript 有什么区别？ |
| **应用架构** | 鸿蒙应用如何设计架构？ |
| **生态前景** | 鸿蒙开发的就业前景如何？ |

---

## ⚠️ 使用限制

### 必须遵守的限制

1. **额度限制**
   - 每个 anonymousId 有试用额度
   - 额度用完需生成新 ID
   - 建议适度使用

2. **频率限制**
   - 遵守 API 速率限制
   - 避免高频请求
   - 失败最多重试 3 次

3. **内容限制**
   - ✅ 仅查询技术问题
   - ❌ 不查询敏感内容
   - ❌ 不传播不当言论

4. **法律限制**
   - ✅ 仅供学习研究
   - ❌ 严禁商业用途
   - ❌ 遵守相关法规

---

## 🛠️ 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| QuotaExceededError | 额度用完 | 生成新 anonymousId |
| NetworkError | 网络问题 | 检查网络连接 |
| DialogError | 对话无效 | 重置对话 |
| TimeoutError | 超时 | 简化问题或稍后重试 |

---

## 📝 响应格式

参考：[templates/response_template.md](templates/response_template.md)

### 标准响应

```
## 📝 华为小艺AI回答

**问题**: [用户问题]

**回答**:
[完整回答]

**参考文档**（如有）:
- [文档链接]

---
查询时间: [时间]
设备ID: [anonymousId]
对话ID: [dialogId]
```

---

## 🔒 法律和安全

### 重要声明

**必须向用户说明：**

- ⚠️ 本工具基于逆向工程，仅供学习研究
- ⚠️ 非华为官方接口
- ⚠️ 请遵守华为开发者联盟使用条款
- ⚠️ 不得用于商业或非法用途

**详细声明见：**
- [免责声明](DISCLAIMER.md)
- [法律声明](docs/LEGAL.md)（待创建）

---

## 🤝 Claude Code 集成

### AI 如何使用本 Skill

当 Claude Code 需要查询鸿蒙开发问题时：

1. **识别场景**
   - 用户询问鸿蒙开发问题
   - 判断是否应该使用本 Skill

2. **读取规则**
   - 读取 SKILL.md 了解使用规则
   - 参考 prompts/query.md 构造问题

3. **执行查询**
   - 调用 scripts/query_xiaoyi.py
   - 使用 Xiaoyi SDK 查询

4. **处理响应**
   - 解析 SSE 流式消息
   - 使用 IncrementalTracker 提取增量
   - 格式化输出

5. **返回结果**
   - 按照 templates/response_template.md 格式化
   - 提供清晰的查询结果

---

## 📚 学习资源

### 官方资源

- 华为开发者官方文档
- 鸿蒙开发社区
- ArkTS 语言指南

### Skill 资源

- [Prompt 模板](prompts/query.md)
- [核心脚本](scripts/query_xiaoyi.py)
- [使用示例](examples/)
- [响应模板](templates/response_template.md)
- [FAQ](docs/FAQ.md)（待创建）

---

## 🔍 常见问题

### Q1: 如何获取更好的回答？

**建议：**
- 问题清晰、具体、技术性强
- 提供必要的上下文
- 使用深度思考模式（`--deep`）

### Q2: 额度用完了怎么办？

**解决方案：**
- Xiaoyi SDK 会自动生成新的 anonymousId
- 或者手动指定新的设备ID

### Q3: 可以查询哪些问题？

**适用范围：**
- ✅ 鸿蒙开发技术问题
- ✅ DevEco Studio 使用问题
- ✅ ArkTS 语言问题
- ✅ 鸿蒙应用架构问题

### Q4: 这个工具是官方的吗？

**不是！**
- ⚠️ 本工具基于逆向工程
- ⚠️ 非华为官方接口
- ⚠️ 仅供学习研究使用

---

## 📜 许可和免责

**仅供学习和研究使用，严禁商业用途。**

详见：
- [LICENSE](../../LICENSE)
- [免责声明](DISCLAIMER.md)

---

## 📞 支持

### 技术支持

- GitHub Issues: 提交问题和反馈
- 文档: 参考 docs/ 目录
- 示例: 查看 examples/ 目录

---

## 🎉 总结

**XiaoYi Query Skill 是一个用于查询鸿蒙开发问题的 Claude Code Skill。**

- ✅ 集成 Xiaoyi SDK
- ✅ 流式查询华为小艺AI
- ✅ 支持多轮对话
- ✅ 支持思维链显示
- ✅ 完整的错误处理

**但请注意：**
- ⚠️ 仅供学习研究
- ⚠️ 非官方接口
- ⚠️ 严禁商业用途
- ⚠️ 使用风险自负

---

**最后提醒：使用前请务必阅读 [免责声明](DISCLAIMER.md)！**