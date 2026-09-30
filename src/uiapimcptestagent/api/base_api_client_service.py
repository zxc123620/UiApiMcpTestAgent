#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/15 17:44
# Author:zhouxiaochuan
# Description:
import logging
import os
import uuid

from jsonpath import jsonpath

from uiapimcptestagent.api.base_api_client import BaseAPIClient
from uiapimcptestagent.api.api_db.api import ApiRepository
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor
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

    # def get_request(self, key: str = "", path: str = "", params=None, headers=None, response_model=None) -> Optional[
    #     requests.Response]:
    #     """
    #     发送get请求
    #     :return:
    #     """
    #     if key != "":
    #         data = ApiTestDataRepository.get_test_data(key)
    #         method, path, params , headers =data.method, data.path, data.request_params,data.request_headers
    #     resp = self.apiclient.get(
    #         endpoint=path,
    #         params=params,
    #         response_model=response_model,
    #         headers=headers or {})
    #     return resp
    #
    # def post_request(self, key: str = None, path: str = None, params=None, json=None, headers=None, response_model=None) -> Optional[
    #     requests.Response]:
    #     """
    #     发送post请求
    #     :return:
    #     """
    #     if key is not None:
    #         data = ApiTestDataRepository.get_test_data(key)
    #         method, path, params ,json, headers =data.method, data.path, data.request_params,data.request_body, data.request_headers
    #     req_data = {
    #         "endpoint": path,
    #         "response_model": response_model,
    #         "headers": headers or {}
    #     }
    #     if params:
    #         req_data["params"] = params
    #     if json:
    #         req_data["json"] = json
    #     resp = cls.apiclient.post(**req_data)
    #     return resp

    def send_request(self, case_id: str):
        """
        发送请求

        Args:
            case_id: 测试用例ID

        Returns:
            None

        """

        # 获取测试用例关联的测试数据
        api_test_data_relations = ApiRepository.get_case_relation_datas(case_id)
        res = None
        # 发起请求
        for api_test_data_relation in api_test_data_relations:
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
            for item in api_test_data_relation.extract:
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
                    #直接赋值jsonpath提取的值
                    StringContextExecutor.context[item.name] = value
                    logging.info(f"提取字段 {item.name} 值: {value}")
                    continue
                # 如果处理方法不是None，调用处理方法
                value_nwe = StringMethodExecutor.methods[item.handle.replace(" ", "")](value, **item.handle_param)
                logging.info(f"提取字段 {item.name} 值: {value_nwe}")
                StringContextExecutor.add_context(item.name, value_nwe)

        return res
