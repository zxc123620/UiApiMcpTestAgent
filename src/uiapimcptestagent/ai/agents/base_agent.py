#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/4 09:46
# Author:zhouxiaochuan
# Description: 基础智能体


import logging
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from uiapimcptestagent.ai.agent_factory import AgentFactory
from uiapimcptestagent.ai.llm_models.deepseek_model import deepseek_llm
from uiapimcptestagent.tools.singleton import Singleton


class BaseAgent(metaclass=Singleton):
    SYSTEM_PROMPT = ""

    def __init__(self, instance_id: str = "BaseAgent", thread_id: str = "BaseAgent", tools: Optional[list] = None,
                 agent_kwargs=None):
        if agent_kwargs is None:
            agent_kwargs = {}
        self.config = {"configurable": {"thread_id": thread_id}}
        self.checkpointer = InMemorySaver()
        self._agent = None
        self.tools = tools or []
        self.agent_kwargs = agent_kwargs

    @property
    def agent(self):
        if self._agent is None:
            self._agent = AgentFactory.create_agent(
                llm=deepseek_llm,
                tools=self.tools,
                system_prompt=self.SYSTEM_PROMPT,
                checkpointer=self.checkpointer,
                **self.agent_kwargs,
            )
        return self._agent

    def stream(self, content: str):
        """
        调用智能体生成测试用例
        Args:
            content: 用户输入的API接口描述

        Returns:

        """
        logging.info("=" * 50)

        for chunk in self.agent.stream(
                input={"messages": [HumanMessage(content)]},
                config=self.config,
                stream_mode="updates",
        ):
            for node_name, update in chunk.items():
                for msg in update.get("messages", []):
                    yield msg

    def invoke(self, content: str):
        """
        调用智能体生成测试用例
        Args:
            content: 用户输入的API接口描述

        Returns:

        """
        return self.agent.invoke(input={"messages": [HumanMessage(content)]}, config=self.config)
