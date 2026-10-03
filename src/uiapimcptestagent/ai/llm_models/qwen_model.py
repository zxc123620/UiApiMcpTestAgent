#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:20
# Author:zhouxiaochuan
# Description:

from langchain_qwq import ChatQwen

qwen_llm = ChatQwen(
    model="qwen35b",
    max_tokens=3_000,
    timeout=None,
    max_retries=2,
)
