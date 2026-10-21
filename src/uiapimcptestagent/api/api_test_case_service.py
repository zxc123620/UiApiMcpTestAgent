#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 17:04
# Author:zhouxiaochuan
# Description:
import json
import logging
from typing import Optional

import allure

from uiapimcptestagent.ai.agents.test_assert_agent import TestAssertAgent
from uiapimcptestagent.ai.ai_res_model.test_assert_res_model import ApiTestAssertResModel
from uiapimcptestagent.api.api_db.api_model import ContextKeyHas, JudgeCriteria, TestSteps, JudgeCriteriaItem
from uiapimcptestagent.api.api_client_service import APiClientService
from uiapimcptestagent.assertion.assertion_engine import AssertionEngine
from uiapimcptestagent.assertion.assertion_rules import AssertionConfig
from uiapimcptestagent.assertion.assertion_tools import APIAssertionTools
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor

class ApiTestCaseService:
    base_api_client_service = APiClientService()
    agent = TestAssertAgent()


    @classmethod
    @allure.step("处理allure信息")
    def handle_allure_info(cls, test_case_model):
        """
        处理allure信息

        Args:
            test_case_model: 测试用例模型

        Returns:

        """
        allure.dynamic.feature(test_case_model.module_name)
        allure.dynamic.story(test_case_model.sub_module_name)
        allure.dynamic.title(test_case_model.title)
        allure.dynamic.description(test_case_model.description)

    @classmethod
    def handle_requisites(cls, requisites: Optional[list] = None):
        """
        处理前置/后置操作

        Args:
            requisites: 前置/后置操作列表

        Returns:

        """
        # 如果前置/后置操作为空，直接返回
        if requisites is None or len(requisites) == 0:
            return
        for pre_requisite in requisites:
            # 执行前置/后置操作
            if pre_requisite.api_res_exist is not None:
                # 校验前置/后置操作响应是否存在
                cls.check_api_res_exist(pre_requisite.api_res_exist, exist=True)
            if pre_requisite.api_res_not_exist is not None:
                # 校验前置/后置操作响应不存在
                cls.check_api_res_exist(pre_requisite.api_res_not_exist, exist=False)
            if pre_requisite.context_key_has is not None:
                # 校验前置/后置操作上下文是否存在指定键
                cls.check_context_key_has(pre_requisite.context_key_has)



    @classmethod
    @allure.step("校验上下文是否存在指定键")
    def check_context_key_has(cls, context_key_has: Optional[list[ContextKeyHas]] = None):
        """
        校验上下文是否存在指定键

        Args:
            context_key_has: 上下文键列表
        Returns:

        """
        if context_key_has is None or len(context_key_has) == 0:
            return
        for context_key in context_key_has:
            if context_key.context_key not in StringContextExecutor.context:
                # 如果上下文不存在指定键，根据steps_after_failure发起请求
                for test_data_key in context_key.steps_after_failure:
                    cls.base_api_client_service.send_request(test_data_key=test_data_key)

    @classmethod
    @allure.step("处理断言配置")
    def handle_assert_config(cls,res_json_body: dict, assertion_config: AssertionConfig,exist=True):
        """
        处理断言配置

        Args:
            res_json_body: 响应体
            assertion_config: 断言配置项
            exist: 是否校验存在 True 校验存在 False 校验不存在

        Returns:

        """
        logging.info(f"校验字段: {assertion_config.model_dump()}")
        failed_rules = []
        base_assert_failed_rules = AssertionEngine.run(response=res_json_body,
                                                       rules=assertion_config.assertion_rules)
        failed_rules.extend(base_assert_failed_rules)
        ai_assertion_rule = assertion_config.ai_assertion_rule
        if ai_assertion_rule is not None and ai_assertion_rule != "":
            # 执行 AI 断言
            try:
                APIAssertionTools.ai_judge(ai_assertion_rule, res_json_body)
            except AssertionError as e:
                failed_rules.append(str(e))
        # 校验规则是存在，并且检验通过  或者 校验规则是验证 不存在，并且检验失败(因为不存在就会失败)
        if (exist and len(failed_rules) == 0) or ((not exist) and len(failed_rules) > 0):
            logging.info(f"前置校验通过")
            return None
        # 校验失败
        logging.info(
            f"前置校验失败，校验规则: {assertion_config.model_dump()}，校验结果: {failed_rules}")
        return failed_rules

    @classmethod
    @allure.step("校验响应是否存在")
    def check_api_res_exist(cls, api_res_exist:Optional[list[JudgeCriteria]] = None, exist=True):
        """
        校验响应是否存在

        Args:
            api_res_exist: 响应是否存在列表
            exist: 是否校验响应是否存在 True 校验存在 False 校验不存在

        Returns:

        """
        if api_res_exist is None or len(api_res_exist) == 0:
            return
        for judge_criteria in api_res_exist:
            # 发起一下请求
            api_res = cls.base_api_client_service.send_request(test_data_key=judge_criteria.test_data_key)
            # 校验字段
            for judgment_criteria_item in judge_criteria.judgment_criteria_items:
                if judgment_criteria_item.assertion_config is None:
                    logging.info(f"校验规则为空，跳过")
                    continue
                if api_res.validated_data is None:
                    logging.info(f"没有响应内容校验，跳过")
                    continue
                # 获取响应内容
                res_json_body = api_res.validated_data.model_dump()
                # 校验响应是否存在
                failed_rules = cls.handle_assert_config(res_json_body, judgment_criteria_item.assertion_config, exist=exist)
                # 表示校验通过
                if failed_rules is None:
                    continue
               # 校验失败
                steps_after_failure = judgment_criteria_item.steps_after_failure
                for steps_after_failure in steps_after_failure:
                    cls.base_api_client_service.send_request(test_data_key=steps_after_failure)


    @classmethod
    @allure.step("处理测试步骤")
    def handle_test_steps(cls, test_steps: Optional[list[TestSteps]] = None):
        """
        处理测试步骤

        Args:
            test_steps: 测试步骤列表

        Returns:

        """
        if test_steps is None or len(test_steps) == 0:
            logging.info("测试步骤为空，跳过")
            return
        for test_step in test_steps:
            # 执行测试步骤
            res = cls.base_api_client_service.send_request(test_data_key=test_step.test_data_key)
            if test_step.assertion_config is None:
                logging.info(f"测试步骤的校验规则为空，跳过")
                continue
            # 校验响应是否存在
            if res.validated_data is None:
                logging.info(f"没有响应内容校验，跳过")
                continue
            # 获取响应内容
            res_json_body = res.validated_data.model_dump()
            # 校验响应数据
            failed_rules = cls.handle_assert_config(res_json_body, test_step.assertion_config)
            # 校验通过
            if failed_rules is None:
                continue
            # 校验失败
            assert len(failed_rules) == 0, f"校验失败，校验规则: {test_step.assertion_config.model_dump()}，校验结果: {failed_rules}"
