#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:20
# Author:zhouxiaochuan
# Description:

from langchain_qwq import ChatQwen

llm = ChatQwen(
    model="qwen35b",
    max_tokens=3_000,
    timeout=None,
    max_retries=2,
    # other params...
)

# 运行智能体
# agent.invoke(
#     {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
# )