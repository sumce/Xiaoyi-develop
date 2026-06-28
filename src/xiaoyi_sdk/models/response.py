"""响应模型"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class ChatResponse:
    """聊天响应结果

    Attributes:
        anonymous_id: 设备ID
        dialog_id: 对话ID
        response: 完整回答文本
        thinking: 思维链内容
        references: 引用来源列表
        code: 状态码
        message: 状态消息

    Examples:
        >>> resp = ChatResponse(
        ...     anonymous_id="xxx",
        ...     dialog_id="yyy",
        ...     response="鸿蒙开发前景很好..."
        ... )
        >>> print(resp.response)
    """

    anonymous_id: str = ""
    dialog_id: str = ""
    response: str = ""
    thinking: str = ""
    references: List[Dict] = field(default_factory=list)
    code: int = 0
    message: str = "成功"

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.code == 0

    @property
    def has_references(self) -> bool:
        """是否有引用"""
        return len(self.references) > 0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "anonymous_id": self.anonymous_id,
            "dialog_id": self.dialog_id,
            "response": self.response,
            "thinking": self.thinking,
            "references": self.references,
            "code": self.code,
            "message": self.message,
        }


@dataclass
class DialogResponse:
    """创建对话响应

    Attributes:
        dialog_id: 对话ID（UUID）
        code: 状态码
        message: 状态消息
    """

    dialog_id: str = ""
    code: int = 0
    message: str = "成功"

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.code == 0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "dialog_id": self.dialog_id,
            "code": self.code,
            "message": self.message,
        }