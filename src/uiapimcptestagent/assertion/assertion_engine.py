#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:46
# Author:zhouxiaochuan
# Description:
# core/assertion_engine.py
import logging
from typing import Any

import allure

from uiapimcptestagent.assertion.assertion_base_operate import OPERATORS
from uiapimcptestagent.assertion.assertion_rules import AssertionRule
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor
from uiapimcptestagent.errors import ContextNotFound
from uiapimcptestagent.tools.response_model_tool import json_extract


# ---------- 对外主入口 ----------
class AssertionEngine:

    @staticmethod
    @allure.step("运行断言规则")
    def run( response: Any, rules: list[AssertionRule], **kwargs) -> list[str]:
        """
        运行一组断言规则，返回失败信息列表（空列表=全通过）
        不抛异常，方便一次性收集所有失败

        Args:
            response: 响应数据
            rules: 断言规则列表

        Returns:
            失败信息列表（空列表=全通过）

        """
        failures = []
        for rule in rules:
            AssertionEngine.run_one(failures, response, rule, **kwargs)
        return failures

    @staticmethod
    def run_one(failures: list[str], response: Any, rule: AssertionRule, **kwargs):
        """
        运行一个断言
        Args:
            failures:
            response:
            rule:

        Returns:

        """
        path = rule.jsonpath
        op = rule.operator
        expected = rule.expect_value
        # 查看是否是上下文变量
        if rule.ctx.get("is_ctx_var", False):
            # 如果是上下文变量,则从上下文获取值
            logging.info(f"上下文变量 {expected} 存在, 从上下文获取值并设置为预期值")
            expected = StringContextExecutor.context.get(expected, None)
            if expected is None:
                # 如果上下文变量不存在,则抛出异常
                raise ContextNotFound(f"上下文变量 {expected} 不存在")
        actual = json_extract(response, path)

        if op not in OPERATORS:
            failures.append(f"未知操作符: {op} (path={path})")
            return

        try:
            logging.info(f"校验操作:{op}, 路径:{path}, 期望:{expected}")
            kwargs["response"] = response
            kwargs["path"] = path
            OPERATORS[op](actual, expected, **kwargs)
        except AssertionError as e:
            logging.info(f"校验失败: {e}")
            failures.append(str(e))
