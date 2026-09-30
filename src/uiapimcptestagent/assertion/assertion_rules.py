#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:50
# Author:zhouxiaochuan
# Description:
from typing import Any

from pydantic import BaseModel, Field


class AssertionRules(BaseModel):
    path: str = Field(default="$",description="JSONPath 表达式")
    op: str = Field(default="eq", description="断言操作符")
    value: Any = Field(..., description="断言值")
