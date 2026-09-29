#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/28 17:24
# Author:zhouxiaochuan
# Description:
import logging

from pydantic import BaseModel

API_RESPONSE_MODEL_REGISTRY: dict[str, type[BaseModel]] = {}

def api_res_model_register(cls):
    """
    注册API响应模型到模型注册器
    """
    logging.info(f"注册API响应模型: {cls.__name__}")
    API_RESPONSE_MODEL_REGISTRY[cls.__name__] = cls
    return cls
