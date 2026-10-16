#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/15 17:44
# Author:zhouxiaochuan
# Description:
import logging
import os
import uuid

import allure
from jsonpath import jsonpath
from sqlalchemy import select
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.api.api_db.api_model import ApiTestDataModel, APiTestDataResExtract
from uiapimcptestagent.api.base_api_client import BaseAPIClient, ApiResponse
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor
from uiapimcptestagent.db.tables import ApiTestData
from uiapimcptestagent.errors import KeyNotFound
from uiapimcptestagent.tools.response_model_tool import API_RESPONSE_MODEL_REGISTRY
from uiapimcptestagent.tools.singleton import Singleton


class APiClientService(metaclass=Singleton):
    """
    基础API服务类
    """

    def __init__(self, *, instance_id: str = "BaseAPiClientService"):
        self.instance_id = instance_id
        self.apiclient = BaseAPIClient(
            api_id=uuid.uuid4().hex,
            base_url=os.getenv("API_BASE_URL") or "http://localhost:8080"
        )

    @allure.step("提取响应字段")
    def extract_resdata(self, extreact_list: list[APiTestDataResExtract], res_json: dict):
        """
        提取响应字段

        Args:
            extreact_list: 提取字段列表
            res_json: 响应数据

        Returns:

        """
        for item in extreact_list:
            # 如果没有实际值，根据jsonpath提取
            value = jsonpath(res_json, item.jsonpath)
            # 如果提取失败，直接返回
            if value is False:
                logging.error(f"提取字段 {item.name} 失败，jsonpath: {item.jsonpath}")
                continue
            # 如果处理方法不是None，调用处理方法
            value_nwe = StringMethodExecutor.methods[item.handle.handle_method](value, **item.handle.handle_param)
            logging.info(f"提取字段 {item.name} 值: {value_nwe}")
            StringContextExecutor.add_context(item.name, value_nwe)

    @allure.step("发送请求")
    def send_request(self, test_data_key: str) -> ApiResponse:
        """
        发送请求

        Args:
            test_data_key: 测试数据key

        Returns:
            None
        Raises:
            KeyNotFound: 测试数据不存在
            ValidationError:
        """

        with Session(db_engine) as session:
            stmt = select(ApiTestData).where(ApiTestData.key == test_data_key)
            db_data = session.execute(stmt).first()
            if db_data is None:
                raise KeyNotFound(f"测试数据 {test_data_key} 不存在")
            api_test_data = ApiTestDataModel.model_validate(db_data)
        # 从注册器中获取响应模型
        response_model = API_RESPONSE_MODEL_REGISTRY.get(api_test_data.api_info.response_model, None)
        # 发起请求
        res = self.apiclient.request(
            method=api_test_data.api_info.method,
            endpoint=api_test_data.api_info.endpoint,
            params=api_test_data.params,
            json=api_test_data.data,
            headers=api_test_data.headers or {},
            response_model=response_model,
        )
        #获取响应json
        res_json = {}
        if res.validated_data is not None:
            res_json = res.validated_data.model_dump()
        # 提取字段
        if api_test_data.extract is not None:
            logging.info(f"提取字段: {api_test_data.extract}")
            self.extract_resdata(api_test_data.extract, res_json)
        # # 校验字段
        # if api_test_data.validate_rules is not None:
        #     logging.info(f"校验字段: {api_test_data.validate_rules}")
        #     failed_rules = AssertionEngine.run(response=res_json, rules=api_test_data.validate_rules)
        #     res.failed_rules = failed_rules
        return res