# 贡献指南

感谢您有兴趣为 Xiaoyi SDK 做出贡献！本文档将帮助您了解如何参与项目开发。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [问题反馈](#问题反馈)

## 行为准则

请阅读并遵守我们的行为准则。我们致力于提供友好、安全和欢迎的环境。

- 尊重所有贡献者
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 如何贡献

### 报告 Bug

如果您发现了 Bug，请通过 [GitHub Issues](https://github.com/xiaoyi-sdk/xiaoyi-sdk/issues) 提交报告。

提交 Bug 报告时，请包含：

1. **清晰的标题** - 简要描述问题
2. **复现步骤** - 详细的步骤让我们能复现问题
3. **期望行为** - 您期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - Python版本、操作系统、SDK版本等
6. **错误日志** - 相关的错误信息和堆栈跟踪

示例：

```markdown
**Bug描述**
调用 chat() 方法时出现 QuotaExceededError

**复现步骤**
1. 安装 xiaoyi-sdk 3.0.0
2. 运行以下代码：
```python
from xiaoyi_sdk import XiaoyiAI
ai = XiaoyiAI()
ai.chat("测试问题")
```
3. 多次重复调用

**期望行为**
正常返回回答

**实际行为**
抛出 QuotaExceededError 异常

**环境**
- Python: 3.10.12
- OS: Windows 11
- SDK: 3.0.0
```

### 提交功能请求

我们欢迎新功能建议！请在 Issue 中详细描述：

1. 功能用途
2. 预期的 API 设计
3. 可能的实现方案

### 提交代码

请阅读以下开发指南。

## 开发环境设置

### 1. Fork 并克隆仓库

```bash
# Fork 后克隆您的仓库
git clone https://github.com/YOUR_USERNAME/xiaoyi-sdk.git
cd xiaoyi-sdk
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 4. 设置 pre-commit 钩子

```bash
pre-commit install
```

## 代码规范

### Python 版本

项目支持 Python 3.8+，请确保代码兼容 Python 3.8。

### 代码风格

我们使用以下工具维护代码质量：

- **black** - 代码格式化
- **isort** - import 排序
- **flake8** - 代码检查
- **mypy** - 类型检查

运行检查：

```bash
# 格式化代码
black src tests
isort src tests

# 代码检查
flake8 src tests

# 类型检查
mypy src
```

### 类型注解

所有公共 API 必须包含类型注解：

```python
def chat(
    self,
    query: str,
    stream: bool = True,
    think_type: int = 1,
) -> Union[Generator[str, None, None], str]:
    """一键式提问"""
    ...
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def create_dialog(self, dialog_type: int = 1001) -> str:
    """创建新对话

    POST /dialog/id → 获取 dialogId

    Args:
        dialog_type: 对话类型 (1001=知识问答)

    Returns:
        dialogId (UUID字符串)

    Raises:
        DialogError: 创建失败

    Examples:
        >>> sess = XiaoyiSession()
        >>> dialog_id = sess.create_dialog()
    """
    ...
```

### 测试

为新功能或 Bug 修复添加测试：

```python
import pytest
from xiaoyi_sdk import XiaoyiAI, generate_anonymous_id


def test_generate_anonymous_id():
    """测试设备ID生成"""
    id1 = generate_anonymous_id()
    assert len(id1) == 32  # MD5长度
    assert id1.isalnum()


def test_generate_anonymous_id_with_seed():
    """测试带种子的设备ID生成"""
    id1 = generate_anonymous_id("test_seed")
    id2 = generate_anonymous_id("test_seed")
    assert id1 == id2  # 相同种子生成相同ID
```

运行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_client.py

# 运行并生成覆盖率报告
pytest --cov=xiaoyi_sdk --cov-report=html
```

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(client): 添加重试机制

- 添加自动重试功能
- 支持自定义重试次数
- 添加重试配置项

Closes #123
```

```
fix(session): 修复连接未正确关闭的问题

修复在异常情况下HTTP连接未正确释放的问题。

Fixes #456
```

## Pull Request 流程

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 进行修改

确保：

- 代码通过所有检查（black, isort, flake8, mypy）
- 添加了必要的测试
- 文档已更新（如有需要）
- 提交消息符合规范

### 3. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

在 GitHub 上创建 Pull Request，填写：

1. **标题** - 清晰描述改动
2. **描述** - 详细说明改动内容和原因
3. **关联 Issue** - 链接相关 Issue
4. **测试** - 说明如何测试

### 4. 代码审查

PR 会被审查，可能需要修改。请：

- 及时回应审查意见
- 按要求修改代码
- 保持讨论专业友好

### 5. 合并

审查通过后，维护者会合并您的 PR。

## 问题反馈

如果您有任何问题，可以：

1. 查看 [FAQ](README.md#常见问题)
2. 搜索 [Issues](https://github.com/xiaoyi-sdk/xiaoyi-sdk/issues)
3. 创建新的 Issue

## 开发提示

### 项目结构

```
xiaoyi-sdk/
├── src/xiaoyi_sdk/    # 源代码
├── tests/             # 测试代码
├── examples/          # 示例代码
├── docs/              # 文档
└── pyproject.toml     # 项目配置
```

### 调试技巧

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

from xiaoyi_sdk import XiaoyiAI

ai = XiaoyiAI()
# ...
```

### 常见问题

**Q: 测试失败怎么办？**

A: 确保安装了所有开发依赖，并检查 Python 版本兼容性。

**Q: 如何运行单个测试？**

A: 使用 `pytest tests/test_file.py::test_function_name`

**Q: pre-commit 钩子失败？**

A: 运行 `pre-commit run --all-files` 查看详细错误。

---

再次感谢您的贡献！ 🎉