#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 14:48
# Author:zhouxiaochuan
# Description:
import logging
import os
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.api.api_db.api_model import ApiTestCaseModel
from uiapimcptestagent.api.api_test_case_service import ApiTestCaseService
from uiapimcptestagent.api.base_api_client import BaseAPIClient
from uiapimcptestagent.db.tables import ApiTestCase


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
        with Session(db_engine) as session:
            # 获取测试用例详情
            stmt = select(ApiTestCase).where(ApiTestCase.key == case_id)
            db_test_case = session.execute(stmt).first()
            test_case_model = ApiTestCaseModel.model_validate(db_test_case)
        # allure报告配置
        ApiTestCaseService.handle_allure_info(test_case_model)
        # 处理前置操作
        ApiTestCaseService.handle_pre_requisites(test_case_model.pre_requisites)
        # 处理测试步骤
        ApiTestCaseService.handle_test_steps(test_case_model.test_steps)
