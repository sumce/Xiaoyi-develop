"""高级客户端API"""

from typing import Generator, Optional, Union

from xiaoyi_sdk.api.session import XiaoyiSession
from xiaoyi_sdk.config import DefaultConfig
from xiaoyi_sdk.models.message import SSEMessage, IncrementalTracker
from xiaoyi_sdk.models.response import ChatResponse
from xiaoyi_sdk.utils.helpers import generate_anonymous_id


class XiaoyiAI:
    """高级客户端：自动管理对话轮次

    自动处理subType切换（首轮=2，后续=1），提供一键式API。

    Examples:
        >>> ai = XiaoyiAI()
        >>> for chunk in ai.chat("鸿蒙前景如何"):
        ...     print(chunk)
        >>> for chunk in ai.chat("那和Java比呢?"):  # 自动跟进
        ...     print(chunk)
        >>> for chunk in ai.chat("新话题", new_dialog=True):  # 重置
        ...     print(chunk)
    """

    def __init__(self, anonymous_id: Optional[str] = None):
        """初始化客户端

        Args:
            anonymous_id: 设备ID（可选，自动生成）
        """
        self._session: Optional[XiaoyiSession] = None
        self._anonymous_id = anonymous_id or generate_anonymous_id()
        self._round = 0

    @property
    def session(self) -> Optional[XiaoyiSession]:
        """当前会话对象"""
        return self._session

    @property
    def anonymous_id(self) -> str:
        """设备ID"""
        return self._anonymous_id

    @property
    def dialog_id(self) -> Optional[str]:
        """当前对话ID"""
        return self._session.dialog_id if self._session else None

    @property
    def round_number(self) -> int:
        """当前对话轮次 (0-based)"""
        return self._round

    def _ensure_session(self):
        """确保会话已创建"""
        if self._session is None:
            self._session = XiaoyiSession(anonymous_id=self._anonymous_id)

    def chat(
        self,
        query: str,
        stream: bool = True,
        think_type: int = DefaultConfig.THINK_TYPE,
        new_dialog: bool = False,
    ) -> Union[Generator[str, None, None], str]:
        """一键式提问

        自动管理：
            - 第一轮 → create_dialog + subType=2
            - 后续轮 → subType=1 (保持上下文)

        Args:
            query: 问题
            stream: 是否流式返回
            think_type: 深度思考开关 (1=开, 0=关)
            new_dialog: 强制开启新对话

        Yields/Returns: SSE data行 或完整响应

        Examples:
            >>> ai = XiaoyiAI()
            >>> for chunk in ai.chat("你好"):
            ...     print(chunk)
        """
        self._ensure_session()

        # 创建新对话或首轮对话
        if new_dialog or self._round == 0:
            self._session.create_dialog()
            self._round = 0

        # 确定subType
        sub_type = 2 if self._round == 0 else 1
        self._round += 1

        return self._session.ask(
            query,
            stream=stream,
            sub_type=sub_type,
            think_type=think_type,
        )

    def chat_with_response(
        self,
        query: str,
        think_type: int = DefaultConfig.THINK_TYPE,
        show_thinking: bool = False,
    ) -> ChatResponse:
        """获取完整响应对象

        Args:
            query: 问题
            think_type: 深度思考开关
            show_thinking: 是否收集思维链

        Returns:
            ChatResponse对象

        Examples:
            >>> ai = XiaoyiAI()
            >>> resp = ai.chat_with_response("你好")
            >>> print(resp.response)
        """
        tracker = IncrementalTracker()
        full_text = ""
        full_thinking = ""
        references = []

        for chunk in self.chat(query, stream=True, think_type=think_type):
            msg = SSEMessage(chunk)

            if msg.is_error:
                raise Exception(msg.error_message)

            if show_thinking and msg.has_thinking:
                delta = tracker.new_thinking(msg)
                if delta:
                    full_thinking += delta

            if msg.has_text:
                delta = tracker.new_text(msg)
                if delta:
                    full_text += delta

            if msg.references:
                references = msg.references

        return ChatResponse(
            anonymous_id=self._anonymous_id,
            dialog_id=self.dialog_id or "",
            response=full_text,
            thinking=full_thinking,
            references=references,
        )

    def reset(self):
        """重置对话状态"""
        self._round = 0
        if self._session:
            self._session.reset_dialog()

    def close(self):
        """关闭会话"""
        if self._session:
            self._session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False