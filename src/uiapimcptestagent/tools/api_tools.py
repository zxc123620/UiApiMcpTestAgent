#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 17:04
# Author:zhouxiaochuan
# Description:
import logging

import allure
from jsonpath import jsonpath

from uiapimcptestagent.api.api_db.api_model import APiTestDataResExtract
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor


@allure.step("提取响应字段")
def extract_resdata(extreact_list: list[APiTestDataResExtract], res_json: dict):
    """
    提取响应字段

    Args:
        extreact_list: 提取字段列表
        res_json: 响应数据

    Returns:

    """
    for item in extreact_list:
        # 如果有实际值，直接赋值
        if item.actual is not None:
            StringContextExecutor.context[item.name] = item.actual
            continue
        # 如果没有实际值，根据jsonpath提取
        value = jsonpath(res_json, item.jsonpath)
        # 如果提取失败，直接返回
        if value is False:
            logging.error(f"提取字段 {item.name} 失败，jsonpath: {item.jsonpath}")
            continue
        # 如果处理方法是None
        if item.handle is None:
            # 直接赋值jsonpath提取的值
            StringContextExecutor.context[item.name] = value
            logging.info(f"提取字段 {item.name} 值: {value}")
            continue
        # 如果处理方法不是None，调用处理方法
        value_nwe = StringMethodExecutor.methods[item.handle.replace(" ", "")](value, **item.handle_param)
        logging.info(f"提取字段 {item.name} 值: {value_nwe}")
        StringContextExecutor.add_context(item.name, value_nwe)