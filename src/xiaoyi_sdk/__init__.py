"""
Xiaoyi SDK - 华为智能客服 Python SDK

提供简洁、类型安全的API接口，支持流式对话、思维链显示等功能。
"""

__version__ = "3.0.0"
__author__ = "sumce"
__email__ = "sumce@example.com"

from xiaoyi_sdk.api.session import XiaoyiSession
from xiaoyi_sdk.api.client import XiaoyiAI
from xiaoyi_sdk.models.message import SSEMessage, IncrementalTracker
from xiaoyi_sdk.models.request import ChatRequest
from xiaoyi_sdk.models.response import ChatResponse
from xiaoyi_sdk.exceptions import (
    XiaoyiError,
    DialogError,
    SubmissionError,
    QuotaExceededError,
)
from xiaoyi_sdk.utils.helpers import generate_anonymous_id

__all__ = [
    "XiaoyiSession",
    "XiaoyiAI",
    "SSEMessage",
    "IncrementalTracker",
    "ChatRequest",
    "ChatResponse",
    "XiaoyiError",
    "DialogError",
    "SubmissionError",
    "QuotaExceededError",
    "generate_anonymous_id",
]