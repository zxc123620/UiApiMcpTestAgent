#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/24 10:06
# Author:zhouxiaochuan
# Description:
import logging
from typing import Literal, Optional, Any

from pydantic import BaseModel, Field, ConfigDict, field_validator

from uiapimcptestagent.assertion.assertion_rules import AssertionRules
from uiapimcptestagent.db.process.string_context_executor import StringContextExecutor
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor

class JsonPathHandle(BaseModel):
    """
    JSONPath 处理方法
    """
    handle_method: str = Field(default="get_index", description='提取字段处理方法')
    handle_param: dict = Field(default_factory=lambda: {"index":0}, description='处理方法参数')

class APiTestDataResExtract(BaseModel):
    """
    API测试数据响应提取字段
    """
    name: str = Field(..., description='提取字段名称')
    jsonpath: str = Field( default="", description='提取字段路径')
    handle: JsonPathHandle = Field(default_factory=JsonPathHandle, description='提取字段处理方法')
    # actual: Optional[Union[list, dict, str, int, float, bool]] = Field( default=None, description='实际值')
    description: str = Field(default="", description='提取字段描述')

class JudgeCriteriaItem(BaseModel):
    """
    前置条件判断标准项
    """
    validate_rules: Optional[AssertionRules] = Field(default=None, description='校验字段规则')
    # handle_param: dict = Field( default_factory=lambda : {}, description='处理方法参数')
    steps_after_failure: list[str] = Field(default_factory=list,
                                           description='前置条件判断失败后执行的步骤,执行什么测试数据键即api_test_data.key')

class JudgeCriteria(BaseModel):
    """
    前置条件判断标准
    """
    test_data_key: str = Field(..., description='测试数据键即api_test_data.key')
    judgment_criteria_items: list[JudgeCriteriaItem] = Field(default_factory=list, description='前置条件判断标准项')

class ContextKeyHas(BaseModel):
    """
    上下文键有
    """
    context_key: str = Field(..., description='上下文键')
    steps_after_failure: list[str] = Field(default_factory=list,
                                           description='上下文键失败后执行的步骤,执行什么测试数据键')

class PreRequisites(BaseModel):
    """
    前置条件
    """
    context_key_has: Optional[list[ContextKeyHas]] = Field(default=None, description='上下文键有')
    api_res_exist: Optional[list[JudgeCriteria]] = Field(default=None, description='API响应判断标准')
    api_res_not_exist: Optional[list[JudgeCriteria]] = Field(default=None, description='API响应判断标准（不存在）')

class TestSteps(BaseModel):
    """
    测试步骤
    """
    test_data_key: str = Field(..., description='测试数据键即api_test_data.key')
    description: str = Field(default="", description='测试步骤描述')
    validate_rules: Optional[list[AssertionRules]] = Field(default=None, description='校验字段')


class ApiTestDataModel(BaseModel):
    """
    API测试数据表
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='ID')
    key: str = Field(..., description='测试数据键')
    name: str = Field(..., description='测试数据名称')
    # module_name: str = Field(..., description='测试模块名称') # 使用ApiInfo.module_name
    # sub_module_name: str = Field(..., description='测试子模块名称') # 使用ApiInfo.sub_module_name
    description: str = Field(default="", description='测试数据描述')
    # api_info_id: int = Field(..., description='关联的API信息ID')
    data: Optional[dict] = Field(default=None, description='请求数据')
    params: Optional[dict] = Field(default=None, description='请求参数')

    headers: Optional[dict] = Field(default=None, description='请求头')
    api_info: ApiInfoModel = Field(..., description='关联的API信息')

    extract: Optional[list[APiTestDataResExtract]] = Field(default=None, description='提取字段')
    # [{"name":"userToken","jsonpath":"$.data.userToken","description": "Authorization鉴权码", "handle":"get_index","handle_param":{"index":0}}]
    # validate_rules: Optional[list[AssertionRules]] = Field(default=None, description='校验字段')




    @field_validator("params", "data", "headers")
    @classmethod
    def data_convert(cls, data=None):
        """
        数据转换-请求参数、请求体、请求头
        """
        if data is None:
            return None
        logging.info(f"数据转换:{data}")
        data_s = StringContextExecutor.data_convert(data) # 数据转换
        data_new = StringMethodExecutor.data_convert(data_s) # 数据方法执行
        logging.info(f"数据转换完成:{data_new}")
        return data_new

class ApiInfoModel(BaseModel):
    """
    API信息表
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='主键ID')
    name: str = Field(..., description='API名称')
    description: str = Field(..., description='API描述')
    endpoint: str = Field(..., description='API端点')
    method: Literal['GET', 'POST', 'PUT', 'DELETE'] = Field(..., description='请求方法')
    response_model: str = Field(..., description='响应模型')
    # validate_rules: Optional[list[AssertionRules]] = Field(default=None, description='校验字段')
    # test_datas: list[ApiTestDataModel] = Field(..., description='关联的测试数据')

class ApiTestCaseModel(BaseModel):
    """
    API测试用例表
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='ID')
    module_name: str = Field(..., description='测试用例模块')
    sub_module_name: str = Field(..., description='测试用例子模块')
    title: str = Field(..., description='测试用例标题')
    description: str = Field(..., description='测试用例描述')
    pre_requisites: Optional[list[PreRequisites]] = Field(default=None, description='前置条件')
    test_steps: list[TestSteps] = Field(..., description='测试步骤')


class ApiCaseDataRelationModel(BaseModel):
    """
    API测试用例数据关联表(暂时不用了)
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='主键ID')
    order: int = Field(..., description='执行顺序从0开始')
    test_data: ApiTestDataModel = Field(..., description='关联的测试数据')
    extract: Optional[list[APiTestDataResExtract]] = Field(default=None, description='提取字段')
    validate_rules: Optional[list[AssertionRules]] = Field(default=None, description='校验字段')
    test_case: ApiTestCaseModel = Field(..., description='关联的测试用例')
