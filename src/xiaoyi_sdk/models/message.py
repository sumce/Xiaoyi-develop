"""SSE消息解析模型"""

import json
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SSEMessage:
    """单条SSE数据解析结果

    Attributes:
        raw: 原始JSON字符串
        code: 返回码 (0=成功)
        is_error: 是否错误
        error_message: 错误描述
        is_final: 对话是否结束
        thinking: AI思维链（累积式）
        text_chunk: 回答文本（累积式）
        references: 引用来源列表

    Examples:
        >>> msg = SSEMessage('{"code":0,"result":{"streamingText":"你好"}}')
        >>> msg.has_text
        True
        >>> msg.text_chunk
        '你好'
    """

    raw: str
    _parsed: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """解析JSON数据"""
        if not self._parsed:
            try:
                self._parsed = json.loads(self.raw)
            except json.JSONDecodeError:
                self._parsed = {}

    @property
    def code(self) -> int:
        """返回状态码"""
        return self._parsed.get("code", -1)

    @property
    def is_error(self) -> bool:
        """是否为错误响应"""
        return self.code != 0

    @property
    def error_message(self) -> str:
        """错误消息"""
        return self._parsed.get("message", "未知错误")

    @property
    def quota_exceeded(self) -> bool:
        """试用额度是否用完"""
        return self.code == 98100021

    @property
    def is_final(self) -> bool:
        """对话是否结束"""
        return self._parsed.get("result", {}).get("isFinal") is True

    @property
    def thinking(self) -> str:
        """AI思维链内容"""
        return self._parsed.get("result", {}).get("thinking", "")

    @property
    def has_thinking(self) -> bool:
        """是否包含思维链"""
        return bool(self.thinking)

    @property
    def text_chunk(self) -> str:
        """回答文本片段"""
        return self._parsed.get("result", {}).get("streamingText", "")

    @property
    def has_text(self) -> bool:
        """是否包含回答文本"""
        return bool(self.text_chunk)

    @property
    def references(self) -> List[dict]:
        """引用来源列表"""
        return self._parsed.get("result", {}).get("resultReferences", [])

    @property
    def step_info(self) -> str:
        """当前推理阶段"""
        return self._parsed.get("result", {}).get("stepInfo", "")

    @property
    def dialog_record_id(self) -> str:
        """对话记录ID"""
        return self._parsed.get("result", {}).get("dialogRecordId", "")

    def to_dict(self) -> dict:
        """转换为字典"""
        return self._parsed.copy()


class IncrementalTracker:
    """SSE累积式字段增量提取器

    streamingText 和 thinking 字段是累积式的
    （每条消息包含前面所有内容+增量），这个类用于提取纯增量部分。

    Examples:
        >>> tracker = IncrementalTracker()
        >>> msg1 = SSEMessage('{"result":{"streamingText":"你好"}}')
        >>> delta1 = tracker.new_text(msg1)  # "你好"
        >>> msg2 = SSEMessage('{"result":{"streamingText":"你好！"}}')
        >>> delta2 = tracker.new_text(msg2)  # "！"
    """

    def __init__(self):
        self._last_text: str = ""
        self._last_thinking: str = ""

    def new_text(self, msg: SSEMessage) -> str:
        """提取新增的回答文本

        Args:
            msg: SSE消息对象

        Returns:
            本次新增的文本
        """
        full = msg.text_chunk
        if full.startswith(self._last_text):
            delta = full[len(self._last_text):]
        else:
            # 文本不连续，重置并返回完整文本
            delta = full
            self._last_text = ""
        self._last_text = full
        return delta

    def new_thinking(self, msg: SSEMessage) -> str:
        """提取新增的思维链内容

        Args:
            msg: SSE消息对象

        Returns:
            本次新增的思维链
        """
        full = msg.thinking
        if full.startswith(self._last_thinking):
            delta = full[len(self._last_thinking):]
        else:
            delta = full
            self._last_thinking = ""
        self._last_thinking = full
        return delta

    def reset_text(self):
        """重置文本追踪器"""
        self._last_text = ""

    def reset_thinking(self):
        """重置思维链追踪器"""
        self._last_thinking = ""

    def reset(self):
        """重置所有追踪器"""
        self.reset_text()
        self.reset_thinking()