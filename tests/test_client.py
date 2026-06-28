# -*- coding: utf-8 -*-
"""XiaoyiAI 高级客户端单元测试

使用Mock模拟底层会话，不依赖真实API。
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from xiaoyi_sdk.api.client import XiaoyiAI
from xiaoyi_sdk.models.response import ChatResponse
from xiaoyi_sdk.config import DefaultConfig


class TestXiaoyiAI:
    """XiaoyiAI测试类"""

    def test_init_default(self):
        """测试默认初始化"""
        ai = XiaoyiAI()
        assert ai.anonymous_id is not None
        assert len(ai.anonymous_id) == 32  # MD5长度
        assert ai.session is None
        assert ai.round_number == 0
        assert ai.dialog_id is None

    def test_init_with_anonymous_id(self):
        """测试使用自定义anonymous_id初始化"""
        custom_id = "custom_device_id_12345"
        ai = XiaoyiAI(anonymous_id=custom_id)
        assert ai.anonymous_id == custom_id

    def test_properties(self):
        """测试属性访问"""
        ai = XiaoyiAI(anonymous_id="test-id")

        # 初始状态
        assert ai.session is None
        assert ai.dialog_id is None
        assert ai.round_number == 0
        assert ai.anonymous_id == "test-id"

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_ensure_session(self, mock_session_class):
        """测试会话自动创建"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        assert ai.session is None

        # 首次调用chat会创建会话
        ai._ensure_session()
        assert ai.session is not None
        mock_session_class.assert_called_once()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_first_round(self, mock_session_class):
        """测试第一轮对话"""
        # Mock会话
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0,"result":{"streamingText":"你好"}}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        chunks = list(ai.chat("你好"))

        # 第一轮应该创建对话
        mock_session.create_dialog.assert_called_once()
        # 应该使用subType=2
        mock_session.ask.assert_called_once()
        call_args = mock_session.ask.call_args
        assert call_args[1]["sub_type"] == 2
        assert ai.round_number == 1

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_follow_up(self, mock_session_class):
        """测试后续对话"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        # 第一轮
        list(ai.chat("问题1"))
        assert ai.round_number == 1

        # 第二轮
        mock_session.ask.reset_mock()
        list(ai.chat("问题2"))
        # 不应该再创建对话
        mock_session.create_dialog.assert_called_once()  # 还是只有一次
        # 应该使用subType=1
        call_args = mock_session.ask.call_args
        assert call_args[1]["sub_type"] == 1
        assert ai.round_number == 2

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_new_dialog(self, mock_session_class):
        """测试强制新对话"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "new-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        # 第一轮
        list(ai.chat("问题1"))
        assert ai.round_number == 1

        # 强制新对话
        mock_session.create_dialog.reset_mock()
        list(ai.chat("问题2", new_dialog=True))
        # 应该重新创建对话
        assert mock_session.create_dialog.call_count == 1
        # 轮次应该重置为1
        assert ai.round_number == 1

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_non_stream(self, mock_session_class):
        """测试非流式对话"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = '{"code":0,"result":{"streamingText":"回答"}}'

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        result = ai.chat("问题", stream=False)

        assert isinstance(result, str)
        mock_session.ask.assert_called_once_with(
            "问题", stream=False, sub_type=2, think_type=DefaultConfig.THINK_TYPE
        )

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_with_think_type(self, mock_session_class):
        """测试自定义思考类型"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter([])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        list(ai.chat("问题", think_type=0))

        call_args = mock_session.ask.call_args
        assert call_args[1]["think_type"] == 0

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_with_response(self, mock_session_class):
        """测试获取完整响应对象"""
        # 模拟多轮SSE消息
        sse_messages = [
            '{"code":0,"result":{"thinking":"让我思考..."}}',
            '{"code":0,"result":{"streamingText":"你好"}}',
            '{"code":0,"result":{"streamingText":"你好！","isFinal":true}}',
        ]

        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(sse_messages)

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        response = ai.chat_with_response("你好", show_thinking=True)

        assert isinstance(response, ChatResponse)
        assert response.response == "你好！"
        assert "让我思考..." in response.thinking
        assert response.dialog_id == "test-dialog-id"

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_with_response_error(self, mock_session_class):
        """测试响应中遇到错误"""
        sse_messages = [
            '{"code":1001,"message":"错误信息"}',
        ]

        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(sse_messages)

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        with pytest.raises(Exception) as exc_info:
            ai.chat_with_response("问题")

        assert "错误信息" in str(exc_info.value)

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_chat_with_response_with_references(self, mock_session_class):
        """测试响应中包含引用"""
        sse_messages = [
            '{"code":0,"result":{"streamingText":"回答","resultReferences":[{"title":"参考1","url":"http://example.com"}]}}',
        ]

        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(sse_messages)

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        response = ai.chat_with_response("问题")

        assert len(response.references) == 1
        assert response.references[0]["title"] == "参考1"

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_reset(self, mock_session_class):
        """测试重置对话状态"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.reset_dialog.return_value = "new-dialog-id"

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        # 先创建一些对话
        list(ai.chat("问题1"))
        assert ai.round_number == 1

        # 重置
        ai.reset()
        assert ai.round_number == 0
        mock_session.reset_dialog.assert_called_once()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_reset_without_session(self, mock_session_class):
        """测试未创建会话时重置"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        ai.reset()

        # 未创建会话时，不应该调用reset_dialog
        mock_session.reset_dialog.assert_not_called()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_close(self, mock_session_class):
        """测试关闭会话"""
        mock_session = MagicMock()

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        list(ai.chat("问题"))  # 触发会话创建

        ai.close()
        mock_session.close.assert_called_once()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_close_without_session(self, mock_session_class):
        """测试未创建会话时关闭"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()
        ai.close()

        # 不应该调用close
        mock_session.close.assert_not_called()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_context_manager(self, mock_session_class):
        """测试上下文管理器"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        with XiaoyiAI() as ai:
            list(ai.chat("问题"))

        mock_session.close.assert_called_once()

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_multiple_chats_same_session(self, mock_session_class):
        """测试多轮对话使用同一会话"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        list(ai.chat("问题1"))
        list(ai.chat("问题2"))
        list(ai.chat("问题3"))

        # 应该只创建一个会话
        assert mock_session_class.call_count == 1
        # 创建一次对话
        assert mock_session.create_dialog.call_count == 1
        # 三次提问
        assert mock_session.ask.call_count == 3

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_round_number_increments(self, mock_session_class):
        """测试轮次递增"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        assert ai.round_number == 0

        list(ai.chat("问题1"))
        assert ai.round_number == 1

        list(ai.chat("问题2"))
        assert ai.round_number == 2

        list(ai.chat("问题3"))
        assert ai.round_number == 3

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_sub_type_sequence(self, mock_session_class):
        """测试subType序列正确"""
        mock_session = MagicMock()
        mock_session.dialog_id = "test-dialog-id"
        mock_session.create_dialog.return_value = "test-dialog-id"
        mock_session.ask.return_value = iter(['{"code":0}'])

        mock_session_class.return_value = mock_session

        ai = XiaoyiAI()

        # 第一轮应该是subType=2
        list(ai.chat("问题1"))
        call1 = mock_session.ask.call_args
        assert call1[1]["sub_type"] == 2

        # 后续应该是subType=1
        list(ai.chat("问题2"))
        call2 = mock_session.ask.call_args
        assert call2[1]["sub_type"] == 1

        list(ai.chat("问题3"))
        call3 = mock_session.ask.call_args
        assert call3[1]["sub_type"] == 1

    @patch("xiaoyi_sdk.api.client.XiaoyiSession")
    def test_anonymous_id_passed_to_session(self, mock_session_class):
        """测试anonymous_id传递给会话"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        ai = XiaoyiAI(anonymous_id="test-anonymous-id")
        ai._ensure_session()

        mock_session_class.assert_called_once_with(anonymous_id="test-anonymous-id")