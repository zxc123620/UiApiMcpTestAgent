#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:50
# Author:zhouxiaochuan
# Description:
from typing import Any

from pydantic import BaseModel, Field


class AssertionRules(BaseModel):
    """
    断言规则
    """
    path: str = Field(default="$",description="JSONPath 表达式")
    operator: str = Field(default="res_contains_data", description="断言操作符")
    expect_value: Any = Field(..., description="预期值")
