#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 17:53
# Author:zhouxiaochuan
# Description:
import os

from langchain_deepseek import ChatDeepSeek

deepseek_llm = None


def get_deepseek_llm():
    global deepseek_llm
    if deepseek_llm is None:
        deepseek_llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-flash"),
            max_tokens=40960,
            max_retries=10,
        )
    return deepseek_llm
