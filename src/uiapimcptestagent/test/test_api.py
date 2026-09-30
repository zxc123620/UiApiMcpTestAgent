#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 14:48
# Author:zhouxiaochuan
# Description:
import os
import uuid

import allure

from uiapimcptestagent.api.base_api_client import BaseAPIClient
from uiapimcptestagent.assertion.assertion_engine import AssertionEngine
from uiapimcptestagent.assertion.assertion_errors import ProjectAssertionError
from uiapimcptestagent.tools.api_tools import extract_resdata
from uiapimcptestagent.api.api_db.api_repository import ApiRepository
from uiapimcptestagent.tools.response_model_tool import API_RESPONSE_MODEL_REGISTRY


class TestApi:

    apiclient = BaseAPIClient(
        api_id=uuid.uuid4().hex,
        base_url=os.getenv("API_BASE_URL") or "http://localhost:8080"
    )

    def test_api(self, case_id: str):
        """
        执行测试用例

        Args:
            case_id: 测试用例ID

        Returns:
            None

        """

        # 获取测试用例关联的测试数据
        api_test_data_relations = ApiRepository.get_case_relation_datas(case_id)
        # 发起请求
        for api_test_data_relation in api_test_data_relations:
            # 配置allure报告
            case_model = api_test_data_relation.test_case
            allure.dynamic.feature(case_model.module)
            allure.dynamic.story(case_model.sub_module)
            allure.dynamic.description(case_model.description)
            allure.dynamic.title(case_model.title)
            api_test_data = api_test_data_relation.test_data
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
            # 提取字段
            if api_test_data_relation.extract is None:
                continue
            res_json = res.validated_data.model_dump()
            extract_resdata(api_test_data_relation.extract, res_json)
            # 校验字段
            if api_test_data_relation.validate_rules is None:
                continue
            failed_rules = AssertionEngine.run(response=res_json, rules=api_test_data_relation.validate_rules)
            if len(failed_rules) > 0:
                raise ProjectAssertionError(f"校验失败: {failed_rules}")
