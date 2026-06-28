# -*- coding: utf-8 -*-
"""数据模型单元测试

测试SSE消息解析、请求/响应模型、增量追踪器等。
"""

import pytest

from xiaoyi_sdk.models.message import SSEMessage, IncrementalTracker
from xiaoyi_sdk.models.request import ChatRequest, DialogRequest
from xiaoyi_sdk.models.response import ChatResponse, DialogResponse
from xiaoyi_sdk.config import DefaultConfig


class TestSSEMessage:
    """SSE消息解析测试类"""

    def test_parse_success_message(self):
        """测试解析成功消息"""
        raw = '{"code":0,"result":{"streamingText":"你好","isFinal":false}}'
        msg = SSEMessage(raw)

        assert msg.code == 0
        assert not msg.is_error
        assert msg.text_chunk == "你好"
        assert msg.has_text
        assert not msg.is_final

    def test_parse_error_message(self):
        """测试解析错误消息"""
        raw = '{"code":1001,"message":"错误信息"}'
        msg = SSEMessage(raw)

        assert msg.code == 1001
        assert msg.is_error
        assert msg.error_message == "错误信息"
        assert not msg.has_text

    def test_parse_quota_exceeded(self):
        """测试解析额度用完消息"""
        raw = '{"code":98100021,"message":"Quota exceeded"}'
        msg = SSEMessage(raw)

        assert msg.code == 98100021
        assert msg.quota_exceeded
        assert msg.is_error

    def test_parse_final_message(self):
        """测试解析结束消息"""
        raw = '{"code":0,"result":{"streamingText":"你好！","isFinal":true}}'
        msg = SSEMessage(raw)

        assert msg.is_final

    def test_parse_thinking_message(self):
        """测试解析思维链消息"""
        raw = '{"code":0,"result":{"thinking":"AI正在思考..."}}'
        msg = SSEMessage(raw)

        assert msg.has_thinking
        assert msg.thinking == "AI正在思考..."

    def test_parse_references(self):
        """测试解析引用来源"""
        raw = '{"code":0,"result":{"resultReferences":[{"title":"参考1","url":"http://example.com"}]}}'
        msg = SSEMessage(raw)

        assert len(msg.references) == 1
        assert msg.references[0]["title"] == "参考1"

    def test_parse_step_info(self):
        """测试解析推理阶段"""
        raw = '{"code":0,"result":{"stepInfo":"正在检索知识库"}}'
        msg = SSEMessage(raw)

        assert msg.step_info == "正在检索知识库"

    def test_parse_dialog_record_id(self):
        """测试解析对话记录ID"""
        raw = '{"code":0,"result":{"dialogRecordId":"record-123"}}'
        msg = SSEMessage(raw)

        assert msg.dialog_record_id == "record-123"

    def test_parse_empty_text(self):
        """测试解析空文本"""
        raw = '{"code":0,"result":{"streamingText":""}}'
        msg = SSEMessage(raw)

        assert not msg.has_text
        assert msg.text_chunk == ""

    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        raw = 'invalid json'
        msg = SSEMessage(raw)

        assert msg.code == -1
        assert msg.is_error
        assert msg._parsed == {}

    def test_parse_empty_string(self):
        """测试解析空字符串"""
        raw = ''
        msg = SSEMessage(raw)

        assert msg.code == -1
        assert msg._parsed == {}

    def test_to_dict(self):
        """测试转换为字典"""
        raw = '{"code":0,"result":{"streamingText":"测试"}}'
        msg = SSEMessage(raw)

        data = msg.to_dict()
        assert data["code"] == 0
        assert data["result"]["streamingText"] == "测试"

    def test_repr(self):
        """测试字符串表示"""
        raw = '{"code":0}'
        msg = SSEMessage(raw)
        # 默认repr会省略_parsed字段
        assert "SSEMessage" in repr(msg)


class TestIncrementalTracker:
    """增量追踪器测试类"""

    def test_track_text_increment(self):
        """测试追踪文本增量"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"streamingText":"你好"}}')
        delta1 = tracker.new_text(msg1)
        assert delta1 == "你好"

        msg2 = SSEMessage('{"code":0,"result":{"streamingText":"你好！"}}')
        delta2 = tracker.new_text(msg2)
        assert delta2 == "！"

        msg3 = SSEMessage('{"code":0,"result":{"streamingText":"你好！欢迎"}}')
        delta3 = tracker.new_text(msg3)
        assert delta3 == "欢迎"

    def test_track_text_reset_on_discontinuity(self):
        """测试文本不连续时重置"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"streamingText":"你好"}}')
        delta1 = tracker.new_text(msg1)
        assert delta1 == "你好"

        # 文本不连续
        msg2 = SSEMessage('{"code":0,"result":{"streamingText":"新内容"}}')
        delta2 = tracker.new_text(msg2)
        assert delta2 == "新内容"  # 重置后返回完整文本

    def test_track_thinking_increment(self):
        """测试追踪思维链增量"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"thinking":"分析"}}')
        delta1 = tracker.new_thinking(msg1)
        assert delta1 == "分析"

        msg2 = SSEMessage('{"code":0,"result":{"thinking":"分析问题"}}')
        delta2 = tracker.new_thinking(msg2)
        assert delta2 == "问题"

    def test_track_thinking_reset_on_discontinuity(self):
        """测试思维链不连续时重置"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"thinking":"思考"}}')
        delta1 = tracker.new_thinking(msg1)
        assert delta1 == "思考"

        msg2 = SSEMessage('{"code":0,"result":{"thinking":"新思路"}}')
        delta2 = tracker.new_thinking(msg2)
        assert delta2 == "新思路"

    def test_reset_text(self):
        """测试重置文本追踪器"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"streamingText":"你好"}}')
        tracker.new_text(msg1)

        tracker.reset_text()

        msg2 = SSEMessage('{"code":0,"result":{"streamingText":"你好"}}')
        delta2 = tracker.new_text(msg2)
        # 重置后应该返回完整文本
        assert delta2 == "你好"

    def test_reset_thinking(self):
        """测试重置思维链追踪器"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"thinking":"思考"}}')
        tracker.new_thinking(msg1)

        tracker.reset_thinking()

        msg2 = SSEMessage('{"code":0,"result":{"thinking":"思考"}}')
        delta2 = tracker.new_thinking(msg2)
        assert delta2 == "思考"

    def test_reset_all(self):
        """测试重置所有追踪器"""
        tracker = IncrementalTracker()

        msg1 = SSEMessage('{"code":0,"result":{"streamingText":"文本","thinking":"思维"}}')
        tracker.new_text(msg1)
        tracker.new_thinking(msg1)

        tracker.reset()

        msg2 = SSEMessage('{"code":0,"result":{"streamingText":"文本","thinking":"思维"}}')
        assert tracker.new_text(msg2) == "文本"
        assert tracker.new_thinking(msg2) == "思维"

    def test_track_empty_text(self):
        """测试追踪空文本"""
        tracker = IncrementalTracker()

        msg = SSEMessage('{"code":0,"result":{"streamingText":""}}')
        delta = tracker.new_text(msg)
        assert delta == ""

    def test_track_empty_thinking(self):
        """测试追踪空思维链"""
        tracker = IncrementalTracker()

        msg = SSEMessage('{"code":0,"result":{"thinking":""}}')
        delta = tracker.new_thinking(msg)
        assert delta == ""


class TestChatRequest:
    """聊天请求测试类"""

    def test_create_request(self):
        """测试创建请求"""
        req = ChatRequest(query="测试问题")
        assert req.query == "测试问题"
        assert req.stream == True
        assert req.think_type == DefaultConfig.THINK_TYPE

    def test_to_dict(self):
        """测试转换为字典"""
        req = ChatRequest(
            query="问题",
            anonymous_id="test-id",
            dialog_id="dialog-id",
            sub_type=1,
            think_type=0
        )

        payload = req.to_dict()
        assert payload["query"] == "问题"
        assert payload["anonymousId"] == "test-id"
        assert payload["dialogId"] == "dialog-id"
        assert payload["subType"] == 1
        assert payload["thinkType"] == 0

    def test_to_dict_excludes_none(self):
        """测试字典排除None值"""
        req = ChatRequest(query="问题")
        payload = req.to_dict()

        assert "anonymousId" not in payload
        assert "dialogId" not in payload

    def test_validate_success(self):
        """测试验证成功"""
        req = ChatRequest(query="正常问题")
        assert req.validate() == True

    def test_validate_empty_query(self):
        """测试验证空问题"""
        req = ChatRequest(query="")
        with pytest.raises(ValueError) as exc_info:
            req.validate()
        assert "query不能为空" in str(exc_info.value)

    def test_validate_whitespace_query(self):
        """测试验证空白问题"""
        req = ChatRequest(query="   ")
        with pytest.raises(ValueError):
            req.validate()

    def test_validate_long_query(self):
        """测试验证过长问题"""
        req = ChatRequest(query="a" * 2001)
        with pytest.raises(ValueError) as exc_info:
            req.validate()
        assert "2000字符" in str(exc_info.value)

    def test_validate_invalid_think_type(self):
        """测试验证无效思考类型"""
        req = ChatRequest(query="问题", think_type=2)
        with pytest.raises(ValueError) as exc_info:
            req.validate()
        assert "think_type必须是0或1" in str(exc_info.value)

    def test_validate_invalid_sub_type(self):
        """测试验证无效提交类型"""
        req = ChatRequest(query="问题", sub_type=3)
        with pytest.raises(ValueError) as exc_info:
            req.validate()
        assert "sub_type必须是1或2" in str(exc_info.value)


class TestDialogRequest:
    """创建对话请求测试类"""

    def test_create_request(self):
        """测试创建请求"""
        req = DialogRequest(anonymous_id="test-id")
        assert req.anonymous_id == "test-id"
        assert req.dialog_type == DefaultConfig.DIALOG_TYPE

    def test_to_dict(self):
        """测试转换为字典"""
        req = DialogRequest(
            anonymous_id="test-id",
            dialog_type=1001,
            origin=0
        )

        payload = req.to_dict()
        assert payload["anonymousId"] == "test-id"
        assert payload["type"] == 1001
        assert payload["origin"] == 0


class TestChatResponse:
    """聊天响应测试类"""

    def test_create_response(self):
        """测试创建响应"""
        resp = ChatResponse(
            anonymous_id="anon-id",
            dialog_id="dialog-id",
            response="回答内容"
        )
        assert resp.anonymous_id == "anon-id"
        assert resp.dialog_id == "dialog-id"
        assert resp.response == "回答内容"
        assert resp.code == 0
        assert resp.is_success

    def test_create_with_thinking(self):
        """测试创建带思维链的响应"""
        resp = ChatResponse(
            response="回答",
            thinking="思维过程"
        )
        assert resp.thinking == "思维过程"

    def test_create_with_references(self):
        """测试创建带引用的响应"""
        refs = [{"title": "参考1", "url": "http://example.com"}]
        resp = ChatResponse(
            response="回答",
            references=refs
        )
        assert len(resp.references) == 1
        assert resp.has_references

    def test_create_error_response(self):
        """测试创建错误响应"""
        resp = ChatResponse(
            code=1001,
            message="错误"
        )
        assert not resp.is_success
        assert resp.message == "错误"

    def test_to_dict(self):
        """测试转换为字典"""
        resp = ChatResponse(
            anonymous_id="anon-id",
            dialog_id="dialog-id",
            response="回答",
            thinking="思维",
            references=[{"title": "ref"}]
        )

        data = resp.to_dict()
        assert data["anonymous_id"] == "anon-id"
        assert data["dialog_id"] == "dialog-id"
        assert data["response"] == "回答"
        assert data["thinking"] == "思维"
        assert len(data["references"]) == 1

    def test_default_values(self):
        """测试默认值"""
        resp = ChatResponse()
        assert resp.anonymous_id == ""
        assert resp.dialog_id == ""
        assert resp.response == ""
        assert resp.thinking == ""
        assert resp.references == []
        assert resp.code == 0
        assert resp.message == "成功"


class TestDialogResponse:
    """创建对话响应测试类"""

    def test_create_response(self):
        """测试创建响应"""
        resp = DialogResponse(dialog_id="dialog-123")
        assert resp.dialog_id == "dialog-123"
        assert resp.is_success

    def test_create_error_response(self):
        """测试创建错误响应"""
        resp = DialogResponse(
            dialog_id="",
            code=1001,
            message="失败"
        )
        assert not resp.is_success
        assert resp.message == "失败"

    def test_to_dict(self):
        """测试转换为字典"""
        resp = DialogResponse(
            dialog_id="dialog-id",
            code=0,
            message="成功"
        )

        data = resp.to_dict()
        assert data["dialog_id"] == "dialog-id"
        assert data["code"] == 0
        assert data["message"] == "成功"

    def test_default_values(self):
        """测试默认值"""
        resp = DialogResponse()
        assert resp.dialog_id == ""
        assert resp.code == 0
        assert resp.message == "成功"