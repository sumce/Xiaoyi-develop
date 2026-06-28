# Xiaoyi SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

华为智能客服 Python SDK - 提供简洁、类型安全的API接口，支持流式对话、思维链显示等功能。

## 特性

- 🚀 **简洁易用** - 一键式API，自动管理对话轮次
- 📡 **流式响应** - 支持SSE流式输出，实时显示AI回复
- 🧠 **思维链显示** - 支持深度思考模式，展示AI推理过程
- 🔒 **类型安全** - 完整的类型注解，支持IDE自动补全
- 📦 **零依赖** - 仅依赖 requests 库
- 🌐 **上下文管理** - 自动维护多轮对话上下文

## 安装

```bash
pip install xiaoyi-sdk
```

或使用 pip 从源码安装：

```bash
git clone https://github.com/sumce/Xiaoyi-develop.git
cd Xiaoyi-develop
pip install -e .
```

## 快速开始

### 基础用法

```python
from xiaoyi_sdk import XiaoyiAI

# 创建客户端
ai = XiaoyiAI()

# 流式对话
for chunk in ai.chat("鸿蒙开发前景如何？"):
    print(chunk, end="", flush=True)

# 继续对话（自动保持上下文）
for chunk in ai.chat("那和Java比呢？"):
    print(chunk, end="", flush=True)
```

### 获取完整响应

```python
from xiaoyi_sdk import XiaoyiAI

with XiaoyiAI() as ai:
    # 获取结构化响应对象
    response = ai.chat_with_response(
        "介绍一下华为云服务",
        show_thinking=True  # 包含思维链
    )

    print(f"回答: {response.response}")
    print(f"思维链: {response.thinking}")
    print(f"引用: {response.references}")
```

### 使用底层会话API

```python
from xiaoyi_sdk import XiaoyiSession

with XiaoyiSession() as session:
    # 创建新对话
    dialog_id = session.create_dialog()
    print(f"对话ID: {dialog_id}")

    # 发送问题
    for chunk in session.ask("什么是ArkUI？"):
        print(chunk, end="", flush=True)
```

## API 文档

### XiaoyiAI - 高级客户端

自动管理对话轮次的高级API。

#### 初始化

```python
from xiaoyi_sdk import XiaoyiAI

ai = XiaoyiAI(anonymous_id="your-device-id")  # 可选设备ID
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `anonymous_id` | `str` | 设备ID（可选，自动生成） |

#### 方法

##### `chat(query, stream=True, think_type=1, new_dialog=False)`

一键式提问。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | `str` | 必填 | 问题内容 |
| `stream` | `bool` | `True` | 是否流式返回 |
| `think_type` | `int` | `1` | 深度思考开关（1=开, 0=关）|
| `new_dialog` | `bool` | `False` | 强制开启新对话 |

**返回值**: 生成器（流式）或字符串（非流式）

##### `chat_with_response(query, think_type=1, show_thinking=False)`

获取完整响应对象。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | `str` | 必填 | 问题内容 |
| `think_type` | `int` | `1` | 深度思考开关 |
| `show_thinking` | `bool` | `False` | 是否收集思维链 |

**返回值**: `ChatResponse` 对象

##### `reset()`

重置对话状态，开始新对话。

##### `close()`

关闭会话，释放资源。

### XiaoyiSession - 底层会话

直接管理HTTP会话的底层API。

#### 方法

##### `create_dialog(dialog_type=1001)`

创建新对话。

**返回值**: `str` - 对话ID

##### `ask(query, stream=True, sub_type=2, think_type=1)`

提交问题并获取回答。

| 参数 | 类型 | 说明 |
|------|------|------|
| `sub_type` | `int` | 2=首轮对话, 1=跟进对话 |

### 数据模型

#### ChatResponse

| 属性 | 类型 | 说明 |
|------|------|------|
| `anonymous_id` | `str` | 设备ID |
| `dialog_id` | `str` | 对话ID |
| `response` | `str` | 完整回答文本 |
| `thinking` | `str` | 思维链内容 |
| `references` | `List[Dict]` | 引用来源列表 |
| `code` | `int` | 状态码 |
| `message` | `str` | 状态消息 |

#### SSEMessage

单条SSE数据解析结果。

| 属性 | 类型 | 说明 |
|------|------|------|
| `raw` | `str` | 原始JSON字符串 |
| `code` | `int` | 返回码 |
| `is_error` | `bool` | 是否错误 |
| `is_final` | `bool` | 对话是否结束 |
| `thinking` | `str` | AI思维链内容 |
| `text_chunk` | `str` | 回答文本片段 |
| `references` | `List[dict]` | 引用来源列表 |

### 异常类

| 异常 | 说明 |
|------|------|
| `XiaoyiError` | 基础异常类 |
| `DialogError` | 对话创建失败 |
| `SubmissionError` | 消息提交失败 |
| `QuotaExceededError` | 试用额度用完 |
| `NetworkError` | 网络连接异常 |
| `ValidationError` | 参数验证异常 |

## 示例

查看 [`examples/`](examples/) 目录获取更多示例：

- [`basic_usage.py`](examples/basic_usage.py) - 基础使用示例
- [`interactive_chat.py`](examples/interactive_chat.py) - 交互式命令行聊天

## 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/sumce/Xiaoyi-develop.git
cd Xiaoyi-develop

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src tests
isort src tests
```

### 类型检查

```bash
mypy src
```

## 项目结构

```
xiaoyi-sdk/
├── src/
│   └── xiaoyi_sdk/
│       ├── api/
│       │   ├── client.py      # 高级客户端
│       │   └── session.py     # 底层会话管理
│       ├── models/
│       │   ├── message.py     # SSE消息解析
│       │   ├── request.py     # 请求模型
│       │   └── response.py    # 响应模型
│       ├── utils/
│       │   └── helpers.py     # 工具函数
│       ├── __init__.py
│       ├── config.py          # 配置常量
│       └── exceptions.py      # 自定义异常
├── examples/
│   ├── basic_usage.py
│   └── interactive_chat.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## 常见问题

### Q: 如何获取设备ID？

SDK会自动生成设备ID（anonymousId），也可以手动指定：

```python
from xiaoyi_sdk import XiaoyiAI, generate_anonymous_id

# 自动生成
ai = XiaoyiAI()

# 手动指定
device_id = generate_anonymous_id()
ai = XiaoyiAI(anonymous_id=device_id)
```

### Q: 额度用完怎么办？

如果遇到 `QuotaExceededError`，需要生成新的设备ID：

```python
from xiaoyi_sdk import XiaoyiAI, generate_anonymous_id

# 生成新ID继续使用
new_id = generate_anonymous_id()
ai = XiaoyiAI(anonymous_id=new_id)
```

### Q: 如何开启/关闭深度思考？

```python
# 开启深度思考
for chunk in ai.chat("问题", think_type=1):
    print(chunk)

# 关闭深度思考（快速模式）
for chunk in ai.chat("问题", think_type=0):
    print(chunk)
```

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 免责声明

本SDK为非官方项目，仅供学习和研究使用。使用本SDK需要遵守华为开发者服务条款。

## 致谢

感谢华为提供的智能客服服务。