#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/7/9 13:48
# Author:zhouxiaochuan
# Description:
from typing import Any


class DataProcess:
    """数据处理类"""

    @classmethod
    def data_replacer(cls, value_str: str) -> Any:
        """
        数据替换
        """
        raise ValueError("请实现数据处理方法")

    @classmethod
    def data_convert(cls, data: dict) -> dict:
        """
        数据转换
        :param data: 原始数据
        :return: 转换后的数据
        """
        # def replacer(match):
        #     key = match.group(1)
        #     keys = key.split(".")
        #     value = cls.context
        #     for k in keys:
        #         value = value.get(k, "")
        #         if value is None:
        #             break
        #     result =  str(value) if value is not None else r"${not_found}"
        #     logging.info(f"将{key} 转换为数据:{result}")
        #     return result
        for key, value in data.items():
            if isinstance(value, dict):
                # 递归处理字典
                data[key] = cls.data_convert(value)
            elif isinstance(value, str):
                # 处理字符串
                data[key] = cls.data_replacer(value)
            elif isinstance(value, list):
                # 处理列表
                result = []
                for i in value:
                    result.append(cls.data_replacer(i))
                data[key] = result

        return data
