#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/28 17:24
# Author:zhouxiaochuan
# Description:
import logging

from pydantic import BaseModel
import re
from typing import Any

from jsonpath_ng import parse as jsonpath_parse
API_RESPONSE_MODEL_REGISTRY: dict[str, type[BaseModel]] = {}

def api_res_model_register(cls):
    """
    注册API响应模型到模型注册器
    """
    logging.info(f"注册API响应模型: {cls.__name__}")
    API_RESPONSE_MODEL_REGISTRY[cls.__name__] = cls
    return cls


# ---------- 提取 ----------
def json_extract(response: Any, path: str):
    """从 response 里按 JSONPath 取值，取不到返回 None"""
    if not path or path == "$":
        return response
    matches = jsonpath_parse(path).find(response)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].value
    return [m.value for m in matches]