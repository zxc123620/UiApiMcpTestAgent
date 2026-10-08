#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/4 18:22
# Author:zhouxiaochuan
# Description: 测试工作流
import logging
from typing import NotRequired

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.config import get_stream_writer
from typing_extensions import TypedDict, Annotated

from uiapimcptestagent.ai.agents.api_test_generator_agent import ApiCaseGeneratorAgent
from uiapimcptestagent.ai.agents.api_test_data_generator_agent import ApiTestDataGeneratorAgent
from langgraph.graph import StateGraph, START, END, add_messages

from uiapimcptestagent.ai.agents.intent_recognition_agent import IntentRecognitionAgent
from uiapimcptestagent.tools.singleton import Singleton


class State(TypedDict):
    text: str
    messages: Annotated[list, add_messages]
    intent: NotRequired[str]


class Workflow(metaclass=Singleton):
    """
    弃用了,后续如果有用再用
    """

    def __init__(self):
        self.builder = StateGraph(State)
        # 添加智能体
        self.intent_recognition_agent = IntentRecognitionAgent(thread_id="workflow-intent")  # 意图识别智能体
        self.api_case_generator_agent = ApiCaseGeneratorAgent(thread_id="workflow-api_case_generator")  # 用例生成智能体
        self.api_test_data_generator_agent = ApiTestDataGeneratorAgent(thread_id="workflow-api_test_data_generator")  # 测试数据生成智能体

        # 添加节点
        self.builder.add_node(
            "api_case_generator_agent_node",
            self.api_case_generator_agent_node,
        )
        self.builder.add_node(
            "api_test_data_generator_agent_node",
            self.api_test_data_generator_agent_node,
        )
        self.builder.add_node(
            "intent_recognition",
            self.intent_recognition,
        )
        self.builder.add_node(
            "other_intent",
            self.other_intent,
        )

        # 连边：入口 -> 节点1 -> 节点2 -> 出口
        self.builder.add_edge(START, "intent_recognition")
        self.builder.add_conditional_edges(
            "intent_recognition",
            self.route_by_intent, {
                "测试用例": "api_case_generator_agent_node",
                "测试数据": "api_test_data_generator_agent_node",
                "其他意图": "other_intent",
            }
        )
        self.builder.add_edge("api_case_generator_agent_node", END)
        self.builder.add_edge("api_test_data_generator_agent_node", END)

        # 编译
        self.graph = self.builder.compile()


    def route_by_intent(self, state: State) -> str:
        """
        根据意图路由
        Args:
            state: 状态对象

        Returns:

        """
        intent = (state.get("intent") or "").strip()
        if "用例" in intent:
            return "测试用例"
        if "数据" in intent:
            return "测试数据"
        return "其他意图"
        # return "测试用例生成"

    def other_intent(self, state: State) -> State:
        """
        其他意图处理
        Args:
            state: 状态对象

        Returns:

        """
        msg = AIMessage("抱歉，我没识别出你想生成/保存测试用例还是数据，请说明一下～")
        return  {"text": state["text"], "messages": [msg]}

    def intent_recognition(self, state: State) -> State:
        """
        意图识别
        Args:
            state: 状态对象

        Returns:

        """
        logging.info(f"意图识别: {state}")
        new_messages = []
        intent = ""
        for message_obj in self.intent_recognition_agent.stream(state["text"]):
            new_messages.append(message_obj)
            logging.info(f"获取到意图识别智能体输出:{message_obj}")
            intent = message_obj.content

        return {"text": state["text"], "messages": new_messages, "intent": intent}

    def api_case_generator_agent_node(self, state: State) -> State:
        """
        用例生成智能体节点
        Args:
            state:

        Returns:

        """
        logging.info(f"用例生成智能体节点: {state}")
        new_messages = []
        writer = get_stream_writer()
        for message_obj in self.api_case_generator_agent.stream(state["text"]):
            logging.info(f"获取到智能体输出:{type(message_obj)} - {message_obj}")
            new_messages.append(message_obj)
            writer(message_obj)
        return {"text": state["text"], "messages": new_messages}

    def api_test_data_generator_agent_node(self, state: State) -> State:
        """
        测试数据生成智能体节点
        Args:
            state:

        Returns:

        """
        logging.info(f"测试数据生成智能体节点: {state}")
        new_messages = []
        writer = get_stream_writer()
        for message_obj in self.api_test_data_generator_agent.stream(state["text"]):
            new_messages.append(message_obj)
            writer(message_obj)
        return {"text": state["text"], "messages": new_messages}

    def stream(self, text: str):
        for msg in self.graph.stream(
                {
                    "text": text,
                    "messages": [HumanMessage(text)]
                },
                stream_mode="custom"
        ):
            yield msg
