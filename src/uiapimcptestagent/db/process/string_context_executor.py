#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/11 17:22
# Author:zhouxiaochuan
# Description:
import datetime
import logging
import re
from typing import Any

from uiapimcptestagent.db.process.data_process import DataProcess


class StringContextExecutor(DataProcess):
    """
    数据上下文
    """
    context: dict = {}

    @classmethod
    def add_context(cls, key, value):
        """
        添加上下文
        :param key: 上下文键
        :param value: 上下文值
        :return:

        Args:
            key:
            value:

        Returns:

        """
        logging.info(f"添加上下文: {key} = {value}")
        cls.context[key] = value

    @staticmethod
    def generally_used_context(key: str = None):
        """
        通用上下文 seconds,milliseconds,datetime_now,date_now,time_now 或者 None
        """
        key = key.replace(" ", "")
        if key == "seconds":
            return int(datetime.datetime.now().timestamp())
        elif key == "milliseconds":
            return int(datetime.datetime.now().timestamp() * 1000)
        elif key == "datetime_now":
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif key == "date_now":
            return datetime.datetime.now().strftime("%Y-%m-%d")
        elif key == "time_now":
            return datetime.datetime.now().strftime("%H:%M:%S")
        else:
            return None

    @classmethod
    def data_replacer(cls, value_str: str) -> Any:
        """
        替换字符串中的数据上下文,递归处理字符串,直到匹配不到
        """
        # value_str = value_str.replace(" ", "") # 可能测试人员测试的时候就是要带空格,所以不能去掉
        match = re.search(r"\$\{(.*?)}", value_str)
        if match is None:
            # 没有匹配到字符串，直接返回原字符串
            return value_str
        key = match.group(1)
        # 先从通用上下文中获取，再从数据上下文中获取
        temp_value = cls.generally_used_context(key)
        keys = key.split(".")
        value = cls.context
        for k in keys:
            # 从数据上下文中获取数据
            if isinstance(value, dict):
                # 如果数据为字典，则从字典中获取数据
                value = value.get(k, None)
            else:
                # 如果数据不是字典，则返回未找到数据
                logging.info(f"要获取的数据: {k} 上一级不是字典，返回默认值: not_found")
                return value_str.replace(match.group(0), "not_found")
            if value is None:
                # 如果数据为空
                if temp_value is not None:
                    # 但是通用上下文中有数据，则从通用上下文中获取数据
                    value = temp_value
                    break
                # 如果数据为空，则返回未找到数据
                logging.info(f"未找到数据: {key} ，返回默认值: not_found")
                return "not_found"
        logging.info(f"从{key} 获取到数据: {value}, 类型为: {type(value)}")
        if isinstance(value, (dict, list, tuple)):
            # 如果的到的数据为字典或列表或元组，则返回数据本身
            return value
        elif isinstance(value, (str, int)):
            # 如果数据为字符串或数字
            if len(match.group(0)) == len(value_str):
                logging.info("匹配到的字符串长度与数据总长度一致")
                # 如果匹配的字符串长度等于数据长度，则返回数据本身 "${info.name_1}" 这种情况
                return value
            else:
                # 如果匹配的字符串长度不等于数据长度，则用数据本身替换匹配的字符串 "123${info.name_1}www" 这种情况,并且递归处理字符串,直到匹配不到
                return cls.data_replacer(value_str.replace(match.group(0), str(value)))
        else:
            logging.info("数据不是字符串、数字、字典、列表、元组，返回默认值: not_found")
            return value_str.replace(match.group(0), "not_found")

    #
    #
    # @classmethod
    # def data_convert(cls, data: dict) -> dict:
    #     """
    #     数据转换
    #     :param data: 原始数据
    #     :return: 转换后的数据
    #     """
    #     # def replacer(match):
    #     #     key = match.group(1)
    #     #     keys = key.split(".")
    #     #     value = cls.context
    #     #     for k in keys:
    #     #         value = value.get(k, "")
    #     #         if value is None:
    #     #             break
    #     #     result =  str(value) if value is not None else r"${not_found}"
    #     #     logging.info(f"将{key} 转换为数据:{result}")
    #     #     return result
    #     for key,value in data.items():
    #         if isinstance(value, dict):
    #             # 递归处理字典
    #             cls.data_convert(value)
    #         elif isinstance(value, str):
    #             # 处理字符串
    #             data[key] = cls.str_replacer(value)
    #         elif isinstance(value, list):
    #             # 处理列表
    #             result = []
    #             for i in range(len(value)):
    #                 result.append(cls.str_replacer(value[i]))
    #             data[key] = result
    #
    #     return data

    @classmethod
    def clear(cls):
        """
        清除上下文
        """
        cls.context.clear()

# if __name__ == '__main__':
#     StringDataContext.context["user"] = 10
#     StringDataContext.context["info"] = {"name_1": "张三"}
#     print(StringDataContext.data_convert("123${info.name_1}www"))
#     print(StringDataContext.data_convert("123${user}www"))
