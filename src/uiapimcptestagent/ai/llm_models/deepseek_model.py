#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 17:53
# Author:zhouxiaochuan
# Description:

from langchain_deepseek import ChatDeepSeek

deepseek_llm = ChatDeepSeek(
    model="deepseek-flash",
    max_tokens=40960,
    max_retries=10,
)