#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 14:48
# Author:zhouxiaochuan
# Description:
import logging
import os
import uuid

import allure
import pytest
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

    @pytest.fixture()
    @allure.step("获取测试用例id")
    def case_id(self,request):
        """
        测试用例id

        Args:
            request: 测试用例id

        Returns:

        """
        return request.param

    @pytest.fixture()
    def api_fixture(self, case_id):
        """
        测试用例fixture

        Args:
            case_id: 测试用例id

        Returns:

        """
        # 获取测试用例关联的测试数据
        with Session(db_engine) as session:
            # 获取测试用例详情
            stmt = select(ApiTestCase).where(ApiTestCase.key == case_id)
            db_test_case = session.scalar(stmt)
            test_case_model = ApiTestCaseModel.model_validate(db_test_case)
        # allure报告配置
        # ApiTestCaseService.handle_allure_info(test_case_model)
        # 处理前置操作
        logging.info("处理前置操作")
        ApiTestCaseService.handle_requisites(test_case_model.pre_requisites)
        # 处理测试步骤
        yield test_case_model
        logging.info("处理后置操作")
        # 处理后置操作
        ApiTestCaseService.handle_requisites(test_case_model.post_steps)

    def test_api(self, api_fixture):
        """
        执行测试用例

        Args:
            api_fixture: 测试用例fixture

        Returns:
            None

        """
        # 处理测试步骤
        test_case_model = api_fixture
        # # 获取测试用例关联的测试数据
        # with Session(db_engine) as session:
        #     # 获取测试用例详情
        #     stmt = select(ApiTestCase).where(ApiTestCase.key == case_id)
        #     db_test_case = session.scalar(stmt)
        #     test_case_model = ApiTestCaseModel.model_validate(db_test_case)
        # allure报告配置
        ApiTestCaseService.handle_allure_info(test_case_model)
        # # 处理前置操作
        # ApiTestCaseService.handle_pre_requisites(test_case_model.pre_requisites)

        ApiTestCaseService.handle_test_steps(test_case_model.test_steps)
