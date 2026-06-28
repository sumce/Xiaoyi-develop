"""自定义异常类"""

from typing import Optional


class XiaoyiError(Exception):
    """基础异常类"""

    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:
        if self.code:
            return f"[错误码 {self.code}] {self.message}"
        return self.message


class DialogError(XiaoyiError):
    """对话创建失败异常"""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message, code)
        self.error_type = "dialog_creation"


class SubmissionError(XiaoyiError):
    """消息提交失败异常"""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message, code)
        self.error_type = "submission"


class QuotaExceededError(SubmissionError):
    """试用额度用完异常 (code=98100021)"""

    def __init__(self, anonymous_id: str):
        message = (
            f"anonymousId [{anonymous_id[:12]}...] "
            f"试用额度已用完，请生成新的设备ID继续使用"
        )
        super().__init__(message, code=98100021)
        self.anonymous_id = anonymous_id


class NetworkError(XiaoyiError):
    """网络连接异常"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, code=-1)
        self.original_error = original_error


class ValidationError(XiaoyiError):
    """参数验证异常"""

    def __init__(self, field: str, reason: str):
        message = f"参数验证失败: {field} - {reason}"
        super().__init__(message)
        self.field = field
        self.reason = reason