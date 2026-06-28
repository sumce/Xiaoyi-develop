"""底层会话管理"""

import json
from typing import Generator, Optional, Union

import requests

from xiaoyi_sdk.config import APIConfig, HeadersConfig, DefaultConfig
from xiaoyi_sdk.exceptions import DialogError, SubmissionError, QuotaExceededError
from xiaoyi_sdk.models.message import SSEMessage
from xiaoyi_sdk.models.request import DialogRequest
from xiaoyi_sdk.models.response import DialogResponse
from xiaoyi_sdk.utils.helpers import generate_anonymous_id


class XiaoyiSession:
    """底层HTTP会话管理类

    管理anonymousId和dialogId，直接对应华为API的请求/响应。

    Examples:
        >>> sess = XiaoyiSession()
        >>> dialog_id = sess.create_dialog()
        >>> for chunk in sess.ask("你好"):
        ...     print(chunk)
    """

    def __init__(self, anonymous_id: Optional[str] = None):
        """初始化会话

        Args:
            anonymous_id: 设备ID（可选，自动生成）
        """
        self.anonymous_id = anonymous_id or generate_anonymous_id()
        self.dialog_id: Optional[str] = None

        # HTTP会话
        self._http = requests.Session()
        self._http.headers.update(HeadersConfig.DEFAULT_HEADERS)

    def create_dialog(self, dialog_type: int = DefaultConfig.DIALOG_TYPE) -> str:
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
        req = DialogRequest(
            anonymous_id=self.anonymous_id,
            dialog_type=dialog_type
        )

        headers = {"Content-Type": "application/json;charset=UTF-8"}

        try:
            resp = self._http.post(
                APIConfig.DIALOG_ID_URL,
                json=req.to_dict(),
                headers=headers,
                timeout=15
            )

            if resp.status_code != 200:
                raise DialogError(
                    f"HTTP {resp.status_code}: {resp.text[:200]}"
                )

            data = resp.json()
            if data.get("code") != 0:
                raise DialogError(
                    f"[{data.get('code')}] {data.get('message', 'unknown')}",
                    code=data.get("code")
                )

            self.dialog_id = data["result"]["dialogId"]
            return self.dialog_id

        except requests.RequestException as e:
            raise DialogError(f"网络请求失败: {e}")

    def ask(
        self,
        query: str,
        stream: bool = True,
        dialog_type: int = DefaultConfig.DIALOG_TYPE,
        sub_type: int = 2,
        think_type: int = DefaultConfig.THINK_TYPE,
    ) -> Union[Generator[str, None, None], str]:
        """提交问题并获取回答

        POST /dialog/submission → SSE流式返回

        Args:
            query: 问题文本
            stream: 是否SSE流式返回
            dialog_type: 对话类型
            sub_type: 2=新对话首轮, 1=跟进
            think_type: 1=深度思考, 0=关闭

        Yields (stream=True): 原始SSE data行 (JSON字符串)
        Returns (stream=False): 所有data行用换行拼接

        Raises:
            RuntimeError: dialogId未创建
            SubmissionError: API返回错误
            QuotaExceededError: 试用额度用完

        Examples:
            >>> sess = XiaoyiSession()
            >>> sess.create_dialog()
            >>> for chunk in sess.ask("你好"):
            ...     print(chunk)
        """
        if not self.dialog_id:
            raise RuntimeError("请先调用 create_dialog()")

        payload = {
            "type": dialog_type,
            "query": query,
            "dialogId": self.dialog_id,
            "channel": DefaultConfig.CHANNEL,
            "origin": DefaultConfig.ORIGIN,
            "subType": sub_type,
            "thinkType": think_type,
            "anonymousId": self.anonymous_id,
        }

        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json;charset=UTF-8",
        }

        try:
            resp = self._http.post(
                APIConfig.SUBMISSION_URL,
                json=payload,
                headers=headers,
                stream=stream,
                timeout=DefaultConfig.TIMEOUT
            )

            if resp.status_code != 200:
                raise SubmissionError(
                    f"HTTP {resp.status_code}: {resp.text[:300]}"
                )

            if stream:
                return self._iter_sse(resp)
            else:
                return self._collect_all(resp)

        except requests.RequestException as e:
            raise SubmissionError(f"网络请求失败: {e}")

    def _iter_sse(self, resp: requests.Response) -> Generator[str, None, None]:
        """SSE流式迭代器

        Args:
            resp: requests响应对象

        Yields:
            SSE data内容 (JSON字符串)
        """
        for line in resp.iter_lines(decode_unicode=True):
            if line is None:
                continue

            line = line.strip()
            if line.startswith("data:"):
                data = line[5:].strip()
                msg = SSEMessage(data)

                if msg.quota_exceeded:
                    raise QuotaExceededError(self.anonymous_id)

                yield data

    def _collect_all(self, resp: requests.Response) -> str:
        """非流式：收集所有data行

        Args:
            resp: requests响应对象

        Returns:
            所有data行用换行拼接
        """
        lines = []
        for line in resp.iter_lines(decode_unicode=True):
            if line is None:
                continue

            line = line.strip()
            if line.startswith("data:"):
                data = line[5:].strip()
                msg = SSEMessage(data)

                if msg.quota_exceeded:
                    raise QuotaExceededError(self.anonymous_id)

                lines.append(data)

        return "\n".join(lines)

    def create_and_ask(
        self,
        query: str,
        dialog_type: int = DefaultConfig.DIALOG_TYPE,
        stream: bool = True,
    ) -> Union[Generator[str, None, None], str]:
        """一键创建对话并提问

        Args:
            query: 问题
            dialog_type: 对话类型
            stream: 是否流式

        Returns:
            SSE流或完整响应

        Examples:
            >>> sess = XiaoyiSession()
            >>> for chunk in sess.create_and_ask("你好"):
            ...     print(chunk)
        """
        self.create_dialog(dialog_type=dialog_type)
        return self.ask(query, stream=stream, dialog_type=dialog_type)

    def reset_dialog(self, dialog_type: int = DefaultConfig.DIALOG_TYPE) -> str:
        """重置为全新对话

        Args:
            dialog_type: 对话类型

        Returns:
            新的dialogId

        Examples:
            >>> sess = XiaoyiSession()
            >>> sess.reset_dialog()
        """
        return self.create_dialog(dialog_type=dialog_type)

    def close(self):
        """关闭HTTP会话"""
        self._http.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False