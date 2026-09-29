#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:39
# Author:zhouxiaochuan
# Description:
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_mcp_adapters.client import MultiServerMCPClient


class Agent:

    @staticmethod
    async def create_agent( llm:BaseChatModel, mcp_client:MultiServerMCPClient, system_prompt: str = "你是一个乐于助人的助手"):
        """
        创建智能体
        Args:
            mcp_client: MCP客户端
            llm: 模型
            system_prompt: 系统提示
        Returns:
        """
        tools = await mcp_client.get_tools()
        create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
        )