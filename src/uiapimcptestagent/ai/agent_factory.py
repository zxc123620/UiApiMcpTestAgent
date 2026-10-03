#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:39
# Author:zhouxiaochuan
# Description:
from typing import Optional, Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel


class AgentFactory:

    @staticmethod
    def create_agent(llm:BaseChatModel, mcp_client:Optional[Any]=None, tools:Optional[list]=None, system_prompt: str = "你是一个乐于助人的助手", *args, **kwargs):
        """
        创建智能体
        Args:
            mcp_client: MCP客户端
            llm: 模型
            tools: 工具
            system_prompt: 系统提示
        Returns:
        """
        all_tools = []
        if mcp_client is not None:
            all_tools.extend(mcp_client.get_tools())
        if tools is not None:
            all_tools.extend(tools)
        return create_agent(
            model=llm,
            tools=all_tools,
            system_prompt=system_prompt,
            *args,
            **kwargs
        )
