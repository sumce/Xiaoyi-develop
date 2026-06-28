"""请求模型"""

from dataclasses import dataclass
from typing import Optional

from xiaoyi_sdk.config import DefaultConfig


@dataclass
class ChatRequest:
    """聊天请求参数

    Attributes:
        query: 用户问题
        anonymous_id: 设备ID（可选，自动生成）
        dialog_id: 对话ID（可选）
        stream: 是否流式返回
        think_type: 思考模式（1=深度思考, 0=快速）
        sub_type: 提交类型（2=首轮, 1=跟进）
        dialog_type: 对话类型（1001=知识问答）

    Examples:
        >>> req = ChatRequest(query="鸿蒙开发前景如何")
        >>> req.to_dict()
        {'query': '鸿蒙开发前景如何', 'stream': True, ...}
    """

    query: str
    anonymous_id: Optional[str] = None
    dialog_id: Optional[str] = None
    stream: bool = True
    think_type: int = DefaultConfig.THINK_TYPE
    sub_type: int = 2
    dialog_type: int = DefaultConfig.DIALOG_TYPE
    channel: int = DefaultConfig.CHANNEL
    origin: int = DefaultConfig.ORIGIN

    def to_dict(self) -> dict:
        """转换为API请求字典"""
        payload = {
            "type": self.dialog_type,
            "query": self.query,
            "dialogId": self.dialog_id,
            "channel": self.channel,
            "origin": self.origin,
            "subType": self.sub_type,
            "thinkType": self.think_type,
            "anonymousId": self.anonymous_id,
        }
        # 移除None值
        return {k: v for k, v in payload.items() if v is not None}

    def validate(self) -> bool:
        """验证请求参数"""
        if not self.query or len(self.query.strip()) == 0:
            raise ValueError("query不能为空")

        if len(self.query) > 2000:
            raise ValueError("query长度不能超过2000字符")

        if self.think_type not in (0, 1):
            raise ValueError("think_type必须是0或1")

        if self.sub_type not in (1, 2):
            raise ValueError("sub_type必须是1或2")

        return True


@dataclass
class DialogRequest:
    """创建对话请求

    Attributes:
        anonymous_id: 设备ID
        dialog_type: 对话类型
        origin: 来源标识
    """

    anonymous_id: str
    dialog_type: int = DefaultConfig.DIALOG_TYPE
    origin: int = DefaultConfig.ORIGIN

    def to_dict(self) -> dict:
        """转换为API请求字典"""
        return {
            "origin": self.origin,
            "type": self.dialog_type,
            "anonymousId": self.anonymous_id,
        }