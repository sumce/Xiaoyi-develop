"""工具函数"""

import hashlib
import time
import uuid
from typing import Optional


def generate_anonymous_id(seed: Optional[str] = None) -> str:
    """生成设备指纹 (anonymousId)

    用于标识游客身份，服务端用它来分配试用额度和追踪对话。

    Args:
        seed: 自定义种子（可选），用于生成确定性ID

    Returns:
        MD5哈希字符串（32字符）

    Examples:
        >>> generate_anonymous_id()
        '9d86177cddccbfcf888002013d4e84f7'
        >>> generate_anonymous_id("test_user")
        '1234567890abcdef1234567890abcdef'
    """
    if seed:
        raw = seed
    else:
        # 模拟浏览器 canvas fingerprint
        raw = f"{uuid.uuid4()}-{time.time_ns()}-{random_string(8)}"

    return hashlib.md5(raw.encode()).hexdigest()


def random_string(length: int = 8) -> str:
    """生成随机字符串

    Args:
        length: 字符串长度

    Returns:
        随机字母数字字符串
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def truncate_text(text: str, max_length: int = 50) -> str:
    """截断文本用于显示

    Args:
        text: 原始文本
        max_length: 最大长度

    Returns:
        截断后的文本（带...）
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """格式化时间戳

    Args:
        timestamp: 时间戳（可选），默认当前时间

    Returns:
        格式化的时间字符串
    """
    from datetime import datetime
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")