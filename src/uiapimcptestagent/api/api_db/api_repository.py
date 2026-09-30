#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 14:51
# Author:zhouxiaochuan
# Description:

import logging

import allure
from sqlalchemy import select
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.api.api_db.api_model import ApiCaseDataRelationModel
from uiapimcptestagent.db.tables import ApiTestCase

class ApiRepository:

    _cache = {}
    @classmethod
    @allure.step("获取测试用例关联的测试数据")
    def get_case_relation_datas(cls, case_id: str):
        """
        获取测试用例关联的测试数据

        Args:
            case_id: 测试用例ID

        Returns:

        """
        # 如果缓存中存在，直接返回缓存中的数据
        if case_id in cls._cache:
            return cls._cache[case_id]
        # 存储测试数据
        api_test_data_relations: list[ApiCaseDataRelationModel] = []
        # sorted_test_datas: list[ApiTestData] = []
        with Session(db_engine) as session:
            # 获取测试用例
            stmt = select(ApiTestCase).where(ApiTestCase.key == case_id)
            single_api_test_case: ApiTestCase | None = session.scalar(stmt)
            # 如果测试用例不存在，直接返回
            if single_api_test_case is None:
                logging.error(f"测试用例 {case_id} not found")
                return None
            # 遍历测试用例关联的测试数据并转换为ApiTestDataModel模型然后存储到api_test_datas中
            for case_relation in single_api_test_case.case_relations:
                api_test_data_relation = ApiCaseDataRelationModel.model_validate(case_relation)
                api_test_data_relations.append(api_test_data_relation)
        # 缓存测试数据
        cls._cache[case_id] = api_test_data_relations
        return api_test_data_relations

