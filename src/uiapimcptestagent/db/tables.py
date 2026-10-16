#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:05
# Author:zhouxiaochuan
# Description:
from sqlalchemy import String, ForeignKey, JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ApiTestData(Base):
    """
    API测试数据表
    """
    __tablename__ = "api_test_data"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
    key: Mapped[str] = mapped_column(String(255), nullable=False,index=True, doc='测试数据键')
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试数据名称')
    description: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试数据描述')
    headers: Mapped[dict] = mapped_column(JSON, nullable=True, doc='请求头')
    api_info_id: Mapped[int] = mapped_column(ForeignKey("api_info.id"), doc='关联的API信息ID')
    data: Mapped[dict] = mapped_column(JSON, nullable=True, doc='请求数据')
    params: Mapped[dict] = mapped_column(JSON, nullable=True, doc='请求参数')
    # module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='模块名称') # 使用ApiInfo.module_name
    # sub_module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='子模块名称') # 使用ApiInfo.sub_module_name
    extract: Mapped[dict] = mapped_column(JSON, nullable=True, doc='提取字段')
    # [{"name":"userToken","jsonpath":"$.data.userToken","description": "Authorization鉴权码", "handle":"get_index","handle_param":{"index":0}}]
    # validate_rules: Mapped[dict] = mapped_column(JSON, nullable=True, doc='校验字段')
    # [{"path":"$","op":"res_contains_data","value":{"userName":"apiTest用户"}}]
    # [{"path":"$","op":"res_contains_data","value":{"status":"0","code":"200","ai.message":"用户名为空"}}]
    # data_relations: Mapped[list["ApiCaseDataRelation"]] = relationship(back_populates="test_data")
    api_info: Mapped['ApiInfo'] = relationship(back_populates="test_datas")


class ApiInfo(Base):
    """
    API信息表
    """
    __tablename__ = "api_info"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc='API名称')
    project_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='项目名称')
    module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='模块名称')
    sub_module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='子模块名称')
    description: Mapped[str] = mapped_column(String(255), nullable=True, doc='API描述')
    endpoint: Mapped[str] = mapped_column(String(255), nullable=True, doc='API端点')
    method: Mapped[str] = mapped_column(String(255), nullable=True, doc='请求方法')
    test_datas: Mapped[list["ApiTestData"]] = relationship(back_populates="api_info")
    response_model: Mapped[str] = mapped_column(String(255), nullable=True, doc='响应模型')
    swagger_md_text: Mapped[str] = mapped_column(Text, nullable=True, doc='SwaggerMarkdown文本')

class ApiTestCase(Base):
    """
    API测试用例表
    """
    __tablename__ = "api_test_case"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
    key: Mapped[str] = mapped_column(String(255), nullable=False,index=True, doc='测试用例键')
    module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例模块')
    sub_module_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例子模块')
    title: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例标题')
    description: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例描述')
    pre_requisites: Mapped[dict] = mapped_column(JSON, nullable=True, doc='前置条件')
    test_steps: Mapped[dict] = mapped_column(JSON, nullable=True, doc='测试步骤')

# class ApiCaseDataRelation(Base):
#     """
#     API测试用例数据关联表（暂时不用）
#     """
#     __tablename__ = "api_case_data_relation"
#     id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True, doc='主键ID')
#     case_id: Mapped[int] = mapped_column(ForeignKey('api_test_case.id'), doc='用例id')
#     order: Mapped[int] = mapped_column(nullable=False, doc='执行顺序从0开始')
#     data_id: Mapped[int] = mapped_column(ForeignKey('api_test_data.id'), doc='数据id')
#     test_data: Mapped["ApiTestData"] = relationship(back_populates="data_relations", doc='关联的测试数据')
#     extract: Mapped[dict] = mapped_column(JSON, nullable=True, doc='提取字段')
#     validate_rules: Mapped[dict] = mapped_column(JSON, nullable=True, doc='校验字段')
#     test_case: Mapped["ApiTestCase"] = relationship(back_populates="case_relations", doc='关联的测试用例')
#
# class AiLLmModels(Base):
#     """
#     Ai LLM模型表（暂时不用）
#     """
#     __tablename__ = "ai_llm_models"
#     id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
#     name: Mapped[str] = mapped_column(String(255), nullable=False,index=True, doc='Ai LLM模型名称')
#     model_name: Mapped[str] = mapped_column(String(255), nullable=True, doc='指定具体模型名称')
#     max_tokens: Mapped[int] = mapped_column(Integer, nullable=True, doc='最大token数')
#     max_retries: Mapped[int] = mapped_column(Integer, nullable=True, doc='最大重试次数')
#     api_key: Mapped[str] = mapped_column(String(255), nullable=True, doc='API密钥')
#     base_url: Mapped[str] = mapped_column(String(255), nullable=True, doc='基础URL')
#     description: Mapped[str] = mapped_column(String(255), nullable=True, doc='模型描述')
#     config: Mapped[dict] = mapped_column(JSON, nullable=True, doc='模型配置')
#
# class AiAgents(Base):
#     """
#     Ai智能体表（暂时不用）
#     """
#     __tablename__ = "ai_agents"
#     id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
#     name: Mapped[str] = mapped_column(String(255), nullable=False,index=True, doc='智能体名称')
#     description: Mapped[str] = mapped_column(String(255), nullable=True, doc='智能体描述')
#     type: # Mapped[str] = mapped_column(String(255), nullable=True, doc="智能体类型")
#     config: Mapped[dict] = mapped_column(JSON, nullable=True, doc='智能体配置')
