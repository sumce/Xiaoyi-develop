# -*- coding: utf-8 -*-
"""XiaoyiSession 单元测试

使用Mock模拟HTTP请求，不依赖真实API。
"""

import json
from typing import Generator
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from xiaoyi_sdk.api.session import XiaoyiSession
from xiaoyi_sdk.exceptions import DialogError, QuotaExceededError, SubmissionError
from xiaoyi_sdk.config import APIConfig, DefaultConfig


class TestXiaoyiSession:
    """XiaoyiSession测试类"""

    def test_init_default(self):
        """测试默认初始化"""
        session = XiaoyiSession()
        assert session.anonymous_id is not None
        assert len(session.anonymous_id) == 32  # MD5长度
        assert session.dialog_id is None

    def test_init_with_anonymous_id(self):
        """测试使用自定义anonymous_id初始化"""
        custom_id = "custom_anonymous_id_12345"
        session = XiaoyiSession(anonymous_id=custom_id)
        assert session.anonymous_id == custom_id

    def test_headers_set(self):
        """测试默认请求头设置"""
        session = XiaoyiSession()
        headers = session._http.headers
        assert "User-Agent" in headers
        assert "Origin" in headers
        assert headers["Origin"] == "https://developer.huawei.com"

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_create_dialog_success(self, mock_session_class):
        """测试创建对话成功"""
        # Mock HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "result": {
                "dialogId": "test-dialog-id-123"
            }
        }

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        dialog_id = session.create_dialog()

        assert dialog_id == "test-dialog-id-123"
        assert session.dialog_id == "test-dialog-id-123"

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_create_dialog_http_error(self, mock_session_class):
        """测试创建对话HTTP错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        with pytest.raises(DialogError) as exc_info:
            session.create_dialog()

        assert "HTTP 500" in str(exc_info.value)

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_create_dialog_api_error(self, mock_session_class):
        """测试创建对话API返回错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 1001,
            "message": "Invalid request"
        }

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        with pytest.raises(DialogError) as exc_info:
            session.create_dialog()

        assert exc_info.value.code == 1001

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_create_dialog_network_error(self, mock_session_class):
        """测试创建对话网络错误"""
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.RequestException("Network error")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        with pytest.raises(DialogError) as exc_info:
            session.create_dialog()

        assert "网络请求失败" in str(exc_info.value)

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_ask_stream_success(self, mock_session_class):
        """测试流式提问成功"""
        # 模拟SSE响应
        sse_data = [
            'data: {"code":0,"result":{"streamingText":"你好"}}',
            'data: {"code":0,"result":{"streamingText":"你好！","isFinal":true}}',
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [line.encode() for line in sse_data]

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "test-dialog-id"

        chunks = list(session.ask("测试问题", stream=True))

        assert len(chunks) == 2
        assert "你好" in chunks[0]

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_ask_non_stream_success(self, mock_session_class):
        """测试非流式提问成功"""
        sse_data = [
            'data: {"code":0,"result":{"streamingText":"回答内容"}}',
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [line.encode() for line in sse_data]

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "test-dialog-id"

        result = session.ask("测试问题", stream=False)
        assert "回答内容" in result

    def test_ask_without_dialog_id(self):
        """测试未创建dialog_id时提问"""
        session = XiaoyiSession()
        with pytest.raises(RuntimeError) as exc_info:
            list(session.ask("测试问题"))

        assert "create_dialog" in str(exc_info.value)

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_ask_quota_exceeded(self, mock_session_class):
        """测试额度用完异常"""
        sse_data = [
            'data: {"code":98100021,"message":"Quota exceeded"}',
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [line.encode() for line in sse_data]

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "test-dialog-id"

        with pytest.raises(QuotaExceededError):
            list(session.ask("测试问题", stream=True))

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_ask_http_error(self, mock_session_class):
        """测试提问HTTP错误"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "test-dialog-id"

        with pytest.raises(SubmissionError):
            list(session.ask("测试问题", stream=True))

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_ask_network_error(self, mock_session_class):
        """测试提问网络错误"""
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.RequestException("Connection failed")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "test-dialog-id"

        with pytest.raises(SubmissionError) as exc_info:
            list(session.ask("测试问题", stream=True))

        assert "网络请求失败" in str(exc_info.value)

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_create_and_ask(self, mock_session_class):
        """测试一键创建对话并提问"""
        # Mock创建对话
        create_response = Mock()
        create_response.status_code = 200
        create_response.json.return_value = {
            "code": 0,
            "result": {"dialogId": "new-dialog-id"}
        }

        # Mock提问
        sse_data = ['data: {"code":0,"result":{"streamingText":"回答"}}']
        ask_response = Mock()
        ask_response.status_code = 200
        ask_response.iter_lines.return_value = [line.encode() for line in sse_data]

        mock_session = MagicMock()
        mock_session.post.side_effect = [create_response, ask_response]
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        chunks = list(session.create_and_ask("问题"))

        assert session.dialog_id == "new-dialog-id"
        assert len(chunks) == 1

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_reset_dialog(self, mock_session_class):
        """测试重置对话"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "result": {"dialogId": "reset-dialog-id"}
        }

        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.dialog_id = "old-dialog-id"

        new_id = session.reset_dialog()

        assert new_id == "reset-dialog-id"
        assert session.dialog_id == "reset-dialog-id"

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_close(self, mock_session_class):
        """测试关闭会话"""
        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        session = XiaoyiSession()
        session.close()

        mock_session.close.assert_called_once()

    @patch("xiaoyi_sdk.api.session.requests.Session")
    def test_context_manager(self, mock_session_class):
        """测试上下文管理器"""
        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        with XiaoyiSession() as session:
            assert session is not None

        mock_session.close.assert_called_once()

    def test_iter_sse_filters_empty_lines(self):
        """测试SSE迭代器过滤空行"""
        session = XiaoyiSession()
        session.dialog_id = "test-id"

        sse_data = [
            None,
            'data: {"code":0}',
            '',
            'data: {"code":0,"result":{"isFinal":true}}',
        ]

        mock_response = Mock()
        mock_response.iter_lines.return_value = sse_data

        chunks = list(session._iter_sse(mock_response))
        assert len(chunks) == 2

    def test_iter_sse_with_thinking(self):
        """测试SSE迭代器处理思维链"""
        session = XiaoyiSession()
        session.dialog_id = "test-id"

        sse_data = [
            'data: {"code":0,"result":{"thinking":"思考中..."}}',
        ]

        mock_response = Mock()
        mock_response.iter_lines.return_value = sse_data

        chunks = list(session._iter_sse(mock_response))
        assert len(chunks) == 1
        data = json.loads(chunks[0])
        assert data["result"]["thinking"] == "思考中..."

    def test_collect_all(self):
        """测试收集所有SSE数据"""
        session = XiaoyiSession()
        session.dialog_id = "test-id"

        sse_data = [
            'data: {"code":0,"result":{"streamingText":"你好"}}',
            'data: {"code":0,"result":{"streamingText":"你好！","isFinal":true}}',
        ]

        mock_response = Mock()
        mock_response.iter_lines.return_value = sse_data

        result = session._collect_all(mock_response)
        lines = result.split("\n")
        assert len(lines) == 2

    def test_ask_uses_correct_payload(self):
        """测试提问使用正确的payload"""
        with patch("xiaoyi_sdk.api.session.requests.Session") as mock_session_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.iter_lines.return_value = []

            mock_session = MagicMock()
            mock_session.post.return_value = mock_response
            mock_session.headers = {}
            mock_session_class.return_value = mock_session

            session = XiaoyiSession(anonymous_id="test-anon-id")
            session.dialog_id = "test-dialog-id"
            list(session.ask("测试问题", sub_type=1, think_type=0))

            call_args = mock_session.post.call_args
            payload = call_args[1]["json"]

            assert payload["query"] == "测试问题"
            assert payload["dialogId"] == "test-dialog-id"
            assert payload["anonymousId"] == "test-anon-id"
            assert payload["subType"] == 1
            assert payload["thinkType"] == 0