#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:46
# Author:zhouxiaochuan
# Description:
# core/assertion_engine.py
import logging
import re
from typing import Any

import allure
from jsonpath_ng import parse as jsonpath_parse

from uiapimcptestagent.assertion.assertion_base_operate import OPERATORS
from uiapimcptestagent.assertion.assertion_rules import AssertionRules


# ---------- 提取 ----------
def _extract(response: Any, path: str):
    """从 response 里按 JSONPath 取值，取不到返回 None"""
    if not path or path == "$":
        return response
    matches = jsonpath_parse(path).find(response)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].value
    return [m.value for m in matches]


# ---------- 对外主入口 ----------
class AssertionEngine:

    @staticmethod
    @allure.step("运行断言规则")
    def run( response: Any, rules: list[AssertionRules]) -> list[str]:
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
            AssertionEngine.run_one(failures, response, rule)
        return failures

    @staticmethod
    def run_one(failures: list[str], response: Any, rule: AssertionRules):
        """
        运行一个断言
        Args:
            failures:
            response:
            rule:

        Returns:

        """
        path = rule.path
        op = rule.op
        expected = rule.value
        actual = _extract(response, path)

        if op not in OPERATORS:
            failures.append(f"未知操作符: {op} (path={path})")
            return

        try:
            logging.info(f"校验操作:{op}, 路径:{path}, 期望:{expected}")
            OPERATORS[op](actual, expected, {
                "response": response, "path": path,
            })
        except AssertionError as e:
            failures.append(str(e))
