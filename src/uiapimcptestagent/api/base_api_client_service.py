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
from uiapimcptestagent.api.api_db.api_model import ApiTestDataModel
from uiapimcptestagent.api.base_api_client import BaseAPIClient, ApiResponse
from uiapimcptestagent.assertion.assertion_engine import AssertionEngine
from uiapimcptestagent.db.tables import ApiTestData
from uiapimcptestagent.errors import KeyNotFound
from uiapimcptestagent.tools.api_tools import extract_resdata
from uiapimcptestagent.tools.response_model_tool import API_RESPONSE_MODEL_REGISTRY
from uiapimcptestagent.tools.singleton import Singleton


class BaseAPiClientService(metaclass=Singleton):
    """
    基础API服务类
    """

    def __init__(self, *, instance_id: str = "BaseAPiClientService"):
        self.instance_id = instance_id
        self.apiclient = BaseAPIClient(
            api_id=uuid.uuid4().hex,
            base_url=os.getenv("API_BASE_URL") or "http://localhost:8080"
        )

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
            extract_resdata(api_test_data.extract, res_json)
        # 校验字段
        if api_test_data.validate_rules is not None:
            logging.info(f"校验字段: {api_test_data.validate_rules}")
            failed_rules = AssertionEngine.run(response=res_json, rules=api_test_data.validate_rules)
            res.failed_rules = failed_rules
        return res