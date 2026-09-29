#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/11 18:14
# Author:zhouxiaochuan
# Description:
import logging
import re
import ast
from functools import wraps
from typing import Any

from uiapimcptestagent.db.process.data_process import DataProcess


class StringMethodExecutor(DataProcess):
    """字符串方法执行器"""
    methods = {}

    @classmethod
    def register(cls, name):
        """注册方法"""

        def wrapper(func):
            cls.methods[name] = func

            @wraps(func)
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return wrapper

    @classmethod
    def _parse_args(cls, args_str: str) -> tuple:
        """解析参数字符串，返回 (args, kwargs)"""
        if not args_str.strip():
            return (), {}

        try:
            # 包装成函数调用的形式来解析
            node = ast.parse(f"fake({args_str})", mode='eval')
            call = node.body
            args = [ast.literal_eval(arg) for arg in call.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
            return args, kwargs
        except:
            # 简单回退：按逗号分割（不处理嵌套）
            raise ValueError("参数解析失败")

    @classmethod
    def execute_method(cls, method_str: str) -> Any:
        """
        执行方法字符串，格式: method_name(args)
        例如: "add(1,2)" 或 "add(1,2,a=3)"
        """
        # 匹配方法名和参数
        match = re.match(r'(\w+)\((.*)\)', method_str.strip())
        if not match:
            raise ValueError(f"无效的方法格式: {method_str}")

        method_name = match.group(1)
        args_str = match.group(2)

        if method_name not in cls.methods:
            raise ValueError(f"未注册的方法: {method_name}")

        # 解析参数
        args, kwargs = cls._parse_args(args_str)
        # 执行方法
        return cls.methods[method_name](*args, **kwargs)

    @classmethod
    def data_replacer(cls, value_str):
        """
        数据替换
        """
        match = re.search(r'__([^(]+\([^)]*\))__', value_str)
        if match is None:
            # 如果没有匹配到方法调用，则返回原字符串
            return value_str
        method_str = match.group(1)  # 提取 method(args)
        logging.info(f"识别到方法调用: {method_str}")
        try:
            result = cls.execute_method(method_str)
            logging.info(f"方法执行结果: {result}")
            if len(match.group(0)) == len(value_str):
                # 如果匹配的字符串长度等于原字符串长度，则返回结果
                # logging.info("匹配的字符串长度等于原字符串长度")
                return result
            else:
                # 如果匹配的字符串长度不等于原字符串长度，则把结果替换到原字符串中的位置
                return cls.data_replacer(value_str.replace(match.group(0), str(result)))
        except Exception as e:
            logging.info(f"执行方法失败: {method_str}, 错误: {e}")
            return value_str  # 保持原样
    #
    # @classmethod
    # def process_string(cls, data: dict) -> str:
    #     """
    #     处理字符串中的 __method(...)__ 格式，替换为执行结果
    #     """
    #     #
    #     # def replacer(match):
    #     #     method_str = match.group(1)  # 提取 method(args)
    #     #     logging.info(f"识别到方法调用: {method_str}")
    #     #     try:
    #     #         result = cls.execute_method(method_str)
    #     #         logging.info(f"方法执行结果: {result}")
    #     #         return str(result)
    #     #     except Exception as e:
    #     #         logging.info(f"执行方法失败: {method_str}, 错误: {e}")
    #     #         return match.group(0)  # 保持原样
    #
    #     # 匹配 __method(...)__ 格式
    #     return re.sub(r'__([^(]+\([^)]*\))__', replacer, text)


@StringMethodExecutor.register("get_index")
def get_index(data:list, index:int=0):
    """
    获取列表索引对应的元素(可在jsonpath提取时使用)
    Args:
        data: 列表
        index: 索引

    Returns:
        元素
    """
    return data[index]

if __name__ == '__main__':
    @StringMethodExecutor.register("method")
    def method(a, b, c):
        print(c)
        return a + b

    text = "__method(1,2,c='hello',d='world')__ + __method(3,4,c='world')__"
    result_1 = StringMethodExecutor.process_string(text)
    print(result_1)
