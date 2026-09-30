#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 13:51
# Author:zhouxiaochuan
# Description:
import re

from uiapimcptestagent.assertion.assertion_tools import APIAssertionTools

# ---------- 操作符实现 ----------
def _op_eq(actual, expected, ctx):
    assert actual == expected, f"期望 {expected!r}, 实际 {actual!r}"

def _op_ne(actual, expected, ctx):
    assert actual != expected, f"期望不等于 {expected!r}, 实际 {actual!r}"

def _op_gt(actual, expected, ctx):
    assert actual > expected, f"期望 > {expected}, 实际 {actual}"

def _op_gte(actual, expected, ctx):
    assert actual >= expected, f"期望 >= {expected}, 实际 {actual}"

def _op_lt(actual, expected, ctx):
    assert actual < expected, f"期望 < {expected}, 实际 {actual}"

def _op_lte(actual, expected, ctx):
    assert actual <= expected, f"期望 <= {expected}, 实际 {actual}"

def _op_exists(actual, expected, ctx):
    assert actual is not None, "期望存在，实际为 None"

def _op_not_exists(actual, expected, ctx):
    assert actual is None, f"期望不存在，实际 {actual!r}"

def _op_type(actual, expected, ctx):
    type_map = {
        "str": str, "int": int, "float": (int, float),
        "bool": bool, "list": list, "dict": dict, "null": type(None),
    }
    assert expected in type_map, f"未知类型: {expected}"
    assert isinstance(actual, type_map[expected]), \
        f"期望类型 {expected}, 实际 {type(actual).__name__}"

def _op_contains(actual, expected, ctx):
    assert expected in actual, f"{actual!r} 不包含 {expected!r}"

def _op_not_contains(actual, expected, ctx):
    assert expected not in actual, f"{actual!r} 不应包含 {expected!r}"

def _op_regex(actual, expected, ctx):
    assert isinstance(actual, str), f"实际值非字符串: {actual!r}"
    assert re.search(expected, actual), \
        f"{actual!r} 不匹配正则 {expected!r}"

def _op_length_eq(actual, expected, ctx):
    assert len(actual) == expected, f"长度期望 {expected}, 实际 {len(actual)}"

def _op_length_gt(actual, expected, ctx):
    assert len(actual) > expected, f"长度期望 > {expected}, 实际 {len(actual)}"

def _op_length_lt(actual, expected, ctx):
    assert len(actual) < expected, f"长度期望 < {expected}, 实际 {len(actual)}"

def _op_in(actual, expected, ctx):
    assert actual in expected, f"{actual!r} 不在 {expected!r} 中"

def _op_not_in(actual, expected, ctx):
    assert actual not in expected, f"{actual!r} 在 {expected!r} 中"

def _op_startswith(actual, expected, ctx):
    assert str(actual).startswith(expected), f"{actual!r} 不以 {expected!r} 开头"

def _op_endswith(actual, expected, ctx):
    assert str(actual).endswith(expected), f"{actual!r} 不以 {expected!r} 结尾"

def _op_between(actual, expected, ctx):
    lo, hi = expected
    assert lo <= actual <= hi, f"{actual} 不在 [{lo}, {hi}] 区间"

def _op_is_empty(actual, expected, ctx):
    assert not actual, f"期望为空，实际 {actual!r}"

def _op_not_empty(actual, expected, ctx):
    assert actual, "期望非空，实际为空"

# def _op_schema(actual, expected, ctx):
#     try:
#         validate(instance=actual, schema=expected)
#     except ValidationError as e:
#         raise AssertionError_(ctx["path"], "schema", expected, actual,
#                               f"Schema 校验失败: {e.message}")
#
# def _op_eq_path(actual, expected, ctx):
#     """actual 应等于另一个 JSONPath 提取的值"""
#     other = _extract(ctx["response"], expected)
#     assert actual == other, f"期望等于 {expected}={other!r}, 实际 {actual!r}"


OPERATORS = {
    "eq": _op_eq, "ne": _op_ne,
    "gt": _op_gt, "gte": _op_gte, "lt": _op_lt, "lte": _op_lte,
    "exists": _op_exists, "not_exists": _op_not_exists,
    "type": _op_type,
    "contains": _op_contains, "not_contains": _op_not_contains,
    "regex": _op_regex,
    "length_eq": _op_length_eq, "length_gt": _op_length_gt, "length_lt": _op_length_lt,
    "in": _op_in, "not_in": _op_not_in,
    "startswith": _op_startswith, "endswith": _op_endswith,
    "between": _op_between,
    "is_empty": _op_is_empty, "not_empty": _op_not_empty,
    "res_contains_data": APIAssertionTools.res_contains_data
    # "schema": _op_schema,
    # "eq_path": _op_eq_path,
}

OPERATORS_KEYWORDS = list(OPERATORS.keys())
