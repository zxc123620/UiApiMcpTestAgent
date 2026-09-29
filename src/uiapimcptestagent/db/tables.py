#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:05
# Author:zhouxiaochuan
# Description:
from sqlalchemy import String, ForeignKey, JSON, Integer
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
    extract: Mapped[dict] = mapped_column(JSON, nullable=True, doc='提取字段')
    data_relations: Mapped[list["ApiCaseDataRelation"]] = relationship(back_populates="test_data")
    api_info: Mapped['ApiInfo'] = relationship(back_populates="test_datas")

class ApiInfo(Base):
    """
    API信息表
    """
    __tablename__ = "api_info"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc='API名称')
    description: Mapped[str] = mapped_column(String(255), nullable=True, doc='API描述')
    endpoint: Mapped[str] = mapped_column(String(255), nullable=True, doc='API端点')
    method: Mapped[str] = mapped_column(String(255), nullable=True, doc='请求方法')
    test_datas: Mapped[list["ApiTestData"]] = relationship(back_populates="api_info")
    response_model: Mapped[str] = mapped_column(String(255), nullable=True, doc='响应模型')

class ApiTestCase(Base):
    """
    API测试用例表
    """
    __tablename__ = "api_test_case"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True, doc='主键ID')
    key: Mapped[str] = mapped_column(String(255), nullable=False,index=True, doc='测试用例键')
    module: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例模块')
    sub_module: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例子模块')
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例名称')
    description: Mapped[str] = mapped_column(String(255), nullable=True, doc='测试用例描述')
    case_relations: Mapped[list["ApiCaseDataRelation"]] = relationship(back_populates="test_case", order_by="ApiCaseDataRelation.order")

class ApiCaseDataRelation(Base):
    """
    API测试用例数据关联表
    """
    __tablename__ = "api_case_data_relation"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True, doc='主键ID')
    case_id: Mapped[int] = mapped_column(ForeignKey('api_test_case.id'), doc='用例id')
    order: Mapped[int] = mapped_column(nullable=False, doc='执行顺序从0开始')
    data_id: Mapped[int] = mapped_column(ForeignKey('api_test_data.id'), doc='数据id')
    test_data: Mapped["ApiTestData"] = relationship(back_populates="data_relations", doc='关联的测试数据')
    test_case: Mapped["ApiTestCase"] = relationship(back_populates="case_relations", doc='关联的测试用例')
