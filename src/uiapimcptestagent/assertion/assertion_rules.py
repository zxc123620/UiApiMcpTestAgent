#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:50
# Author:zhouxiaochuan
# Description:
from typing import Any, Optional
from pydantic import BaseModel, Field


class AssertionRule(BaseModel):
    """单条断言规则"""
    jsonpath: str = Field(default="$", description="JSONPath 表达式(支持所有的JSONPath表达式语法)")
    operator: str = Field(default="res_contains_data", description="断言操作符")
    expect_value: Any = Field(..., description="预期值,可以是任意类型,也可以是系统上下文变量(字符串类型)。如果是上下文变量,只需要填入键名(注意不需要${})，并且在ctx中添加一个字段名`is_ctx_var`的,并设置为True")
    ctx: dict = Field(default_factory=dict, description="其他上下文信息(如果expect_value是一个系统上下文变量,则这里需要添加一个字段名`is_ctx_var`的,并设置为True)")


class AIAssertionRule(BaseModel):
    """单条 AI 断言规则"""


class AssertionConfig(BaseModel):
    """完整的断言配置（普通规则列表 + AI 规则）"""

    assertion_rules: list[AssertionRule] = Field(..., description="断言规则列表")
    ai_assertion_rule: Optional[str] = Field(
        default=None,
        description="AI 断言内容，例如：'响应体包含xxx字段'、'响应体包含xxx字段且值为123'、'响应体xxx字段应该与xxx语义相符' 等",
    )