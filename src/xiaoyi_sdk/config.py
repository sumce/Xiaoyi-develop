"""配置常量和默认值"""

from typing import Final


class APIConfig:
    """API端点配置"""

    BASE_URL: Final[str] = "https://svc-drcn.developer.huawei.com/intelligentcustomer/v1/public"
    DIALOG_ID_URL: Final[str] = f"{BASE_URL}/dialog/id"
    SUBMISSION_URL: Final[str] = f"{BASE_URL}/dialog/submission"
    ANALYTICS_URL: Final[str] = "https://metrics-drcn.dt.hicloud.com:6447/webv2"


class HeadersConfig:
    """默认请求头"""

    USER_AGENT: Final[str] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    ORIGIN: Final[str] = "https://developer.huawei.com"
    REFERER: Final[str] = "https://developer.huawei.com/"
    ACCEPT_LANGUAGE: Final[str] = "zh-CN,zh;q=0.9"

    DEFAULT_HEADERS: Final[dict] = {
        "User-Agent": USER_AGENT,
        "Origin": ORIGIN,
        "Referer": REFERER,
        "Accept-Language": ACCEPT_LANGUAGE,
    }


class DefaultConfig:
    """API调用默认参数"""

    CHANNEL: Final[int] = 1
    ORIGIN: Final[int] = 0
    THINK_TYPE: Final[int] = 1  # 1=深度思考, 0=快速
    DIALOG_TYPE: Final[int] = 1001  # 知识问答类型
    TIMEOUT: Final[int] = 120  # SSE超时（秒）
    MAX_RETRIES: Final[int] = 3


class ErrorCode:
    """错误码定义"""

    SUCCESS: Final[int] = 0
    QUOTA_EXCEEDED: Final[int] = 98100021
    INVALID_DIALOG: Final[int] = 98100001
    NETWORK_ERROR: Final[int] = -1