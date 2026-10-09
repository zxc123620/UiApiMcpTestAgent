#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:20
# Author:zhouxiaochuan
# Description:
import os

from langchain_qwq import ChatQwen

qwen_llm = None

def get_qwen_llm():
    global qwen_llm
    if qwen_llm is None:
        qwen_llm = ChatQwen(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen35b"),
            max_tokens=40_000,
            max_retries=2,
        )
    return qwen_llm

