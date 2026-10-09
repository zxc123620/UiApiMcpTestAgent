#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 10:32
# Author:zhouxiaochuan
# Description:
import logging
from encodings import palmos
from typing import Sequence, Optional

from langchain.tools import tool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor
from uiapimcptestagent.db.tables import ApiInfo, ApiTestCase, ApiTestData, ApiCaseDataRelation


@tool
def get_api_swagger_md_text(project_name: str, module_name: str, sub_module_name: str, api_name: str) -> str:
    """
    获取指定项目的指定模块、指定子模块、指定API的Markdown文本描述(可能是多个)
    Args:
        project_name: 项目名称
        module_name: 模块名称
        sub_module_name: 子模块名称
        api_name: API名称

    Returns:
        md格式Api接口描述字符串
    """
    logging.info(
        f"获取Api接口描述: 项目={project_name}, 模块={module_name}, 子模块={sub_module_name}, API名称={api_name}")
    result = "未找到指定的Api接口描述。"
    with Session(db_engine) as session:
        stmt = select(ApiInfo.swagger_md_text)
        if project_name:
            stmt = stmt.where(ApiInfo.project_name.like(f"%{project_name}%"))
        if module_name:
            stmt = stmt.where(ApiInfo.module_name.like(f"%{module_name}%"))
        if sub_module_name:
            stmt = stmt.where(ApiInfo.sub_module_name.like(f"%{sub_module_name}%"))
        if api_name:
            stmt = stmt.where(ApiInfo.name.like(f"%{api_name}%"))
        db_results = session.scalars(stmt).all()
        if db_results:
            result = f"共{len(db_results)}个Api接口描述\n"
            for index, db_result in enumerate(db_results):
                result += f"第{index + 1}个Api接口描述 \n{db_result}\n"
    logging.info(result)
    return result

@tool
def get_api_summary(module_name: Optional[str] = None, sub_module_name: Optional[str] = None) -> str:
    """
    获取所有API接口的项目、模块、子模块、API名称、接口路径、请求方法
    Args:
        module_name: 模块名称,可选
        sub_module_name: 子模块名称,可选

    Returns:
    """
    logging.info(f"获取所有API接口摘要: 模块={module_name}, 子模块={sub_module_name}")
    result = "未找到指定的API接口摘要。"
    with Session(db_engine) as session:
        stmt = select(ApiInfo)
        if module_name:
            stmt = stmt.where(ApiInfo.module_name.like(f"%{module_name}%"))
        if sub_module_name:
            stmt = stmt.where(ApiInfo.sub_module_name.like(f"%{sub_module_name}%"))
        rows = session.scalars(stmt).all()
        if rows:
            result = f"共{len(rows)}个Api接口摘要\n"
            for index, row in enumerate(rows):
                result += f"第{index + 1}个Api接口摘要: id={row.id}, 项目={row.project_name}, 模块={row.module_name}, 子模块={row.sub_module_name}, API名称={row.name}, 接口路径:{row.endpoint}\n, 请求方法:{row.method}\n"
    logging.info(result)
    return result

@tool
def save_api_test_case(key: str, title: str, description: str, module_name: str, sub_module_name: str) -> str:
    """
    保存API接口的测试用例到数据库
    Args:
        key: 用例的唯一标识
        title: 用例的名称
        description: 用例的详细描述
        module_name: 模块名称(中文)
        sub_module_name : 子模块名称(中文)

    Returns:
        保存结果
    """
    logging.info(f"保存测试用例: {key}, {title}, {description}, {module_name}, {sub_module_name}")
    try:
        with Session(db_engine) as session:
            session.add(
                ApiTestCase(
                    key=key,
                    title=title,
                    description=description,
                    module_name=module_name,
                    sub_module_name=sub_module_name
                ))
            session.commit()
    except IntegrityError as e:
        # 比如唯一约束冲突
        logging.error(e)
        return f"保存失败：{key} 可能已存在。错误：{e}"
    except Exception as e:
        logging.error(e)
        return f"保存失败：{e}"

    return f"成功保存测试用例: {key}, {title}, {description}, {module_name}, {sub_module_name}"

@tool
def get_api_test_case(module_name: Optional[str] = None, sub_module_name: Optional[str] = None) -> str:
    """
    获取指定模块、指定子模块的所有API接口测试用例
    Args:
        module_name: 模块名称(中文)
        sub_module_name: 子模块名称(中文)

    Returns:
        所有API接口测试用例的列表
        每个测试用例包含id,key,模块名称,子模块名称,用例名称,用例描述
    """
    logging.info(f"获取API接口的测试用例: 模块={module_name}, 子模块={sub_module_name}")
    result = "未找到指定的API接口测试用例。"
    with Session(db_engine) as session:
        stmt = select(ApiTestCase)
        if module_name:
            stmt = stmt.where(ApiTestCase.module_name.like(f"%{module_name}%"))
        if sub_module_name:
            stmt = stmt.where(ApiTestCase.sub_module_name.like(f"%{sub_module_name}%"))
        db_results = session.scalars(stmt).all()
        if db_results:
            result = f"共{len(db_results)}条测试用例\n"
            for index, db_result in enumerate(db_results):
                result += f"第{index + 1}条测试用例: id={db_result.id},key={db_result.key}, 模块名称={db_result.module_name}, 子模块名称={db_result.sub_module_name}, 用例名称={db_result.title}, 用例描述={db_result.description}\n"
    logging.info(result)
    return result

@tool
def get_all_modules() -> str:
    """
    获取所有API接口的模块信息
       Returns:
        所有API接口的模块信息列表
    """
    logging.info("获取所有API接口的模块名称")

    result = "未找到指定的API接口模块名称。"
    with Session(db_engine) as session:
        stmt = select(ApiInfo).distinct()
        db_results = session.scalars(stmt).all()
        if db_results:
            result = f"共{len(db_results)}个子模块名称\n"
            for index, db_result in enumerate(db_results):
                result += f"第{index + 1}个: 模块名称={db_result.module_name}, 子模块名称={db_result.sub_module_name}\n"
    logging.info(result)
    return result

@tool
def save_api_test_data(key: str, name: str, module_name: str, sub_module_name: str ,description: str, headers: dict, api_info_id: int, data: dict, params: dict) -> str:
    """
    保存API接口的测试数据到数据库
    Args:
        key: 测试数据的唯一标识
        name: 测试数据的名称
        module_name: 模块名称(中文)
        sub_module_name: 子模块名称(中文)
        description: 测试数据的详细描述,没有就是None
        headers: 请求头,json数据,没有就是None
        api_info_id: API接口的id
        data: 请求数据,json数据,没有就是None
        params: 请求参数,json数据,没有就是None

    Returns:
        保存结果
    """
    logging.info(f"保存测试数据: {key}, {name}, {description}, {headers}, {api_info_id}, {data}, {params}")
    try:
        with Session(db_engine) as session:
            session.add(
                ApiTestData(
                    key=key,
                    name=name,
                    module_name=module_name,
                    sub_module_name=sub_module_name,
                    description=description,
                    headers=headers,
                    api_info_id=api_info_id,
                    data=data,
                    params=params
                ))
            session.commit()
    except IntegrityError as e:
        # 比如唯一约束冲突
        return f"保存失败：{key} 可能已存在。错误：{e}"
    except Exception as e:
        return f"保存失败：{e}"

    return f"成功保存测试数据: {key}, {name}, {description}, {headers}, {api_info_id}, {data}, {params}"

@tool
def search_api_test_data(data_like: Optional[str] = None, module_name: Optional[str] = None, sub_module_name: Optional[str] = None) -> str:
    """
    查询测试数据
    Args:
        data_like: 请求体的字符串,可选,没有就是None
        module_name: 模块名称(中文),可选,没有就是None
        sub_module_name: 子模块名称(中文),可选,没有就是None

    Returns:
        测试数据的列表
        每个测试数据包含id,key,名称,描述,请求头,API接口id,请求数据,请求参数
    """
    logging.info(f"根据请求体字符串模糊查询测试数据: {data_like}, 模块={module_name}, 子模块={sub_module_name}")
    result = "未找到指定的测试数据。"
    with Session(db_engine) as session:
        stmt = select(ApiTestData)
        if data_like:
            stmt = stmt.where(ApiTestData.data.like(f"%{data_like}%"))
        if module_name:
            stmt = stmt.where(ApiTestData.module_name.like(f"%{module_name}%"))
        if sub_module_name:
            stmt = stmt.where(ApiTestData.sub_module_name.like(f"%{sub_module_name}%"))
        db_results = session.scalars(stmt).all()
        if db_results:
            result = f"共{len(db_results)}条测试数据\n"
            for index, db_result in enumerate(db_results):
                result += f"第{index + 1}条测试数据: id={db_result.id},key={db_result.key}, 名称={db_result.name}, 描述={db_result.description}, 请求头={db_result.headers}, API接口id={db_result.api_info_id}, 请求数据={db_result.data}, 请求参数={db_result.params}\n"
    logging.info(result)
    return result

@tool
def get_func_helper():
    """
    获取所有的函数帮助信息
    Returns:
        所有函数帮助信息的列表
        每个函数帮助信息包含函数名称,描述。描述中包含参数,返回值,异常等信息。
    """
    logging.info("获取所有的函数帮助信息")
    return StringMethodExecutor.get_func_doc()


@tool
def get_context_data():
    """
    获取测试系统中所有的上下文数据
    Returns:

    """
    logging.info("获取所有的上下文数据")
    with Session(db_engine) as session:
        stmt = select(ApiCaseDataRelation.extract).where(ApiCaseDataRelation.extract != "", ApiCaseDataRelation.extract.isnot(None))
        db_results = session.scalars(stmt).all()
        if db_results:
            result = f"共{len(db_results)}个上下文数据\n"
            for index, extract_datas in enumerate(db_results):
                # logging.info(f"extract_datas：{extract_datas}")
                for extract_data in extract_datas:
                    result += f"上下文名称:{extract_data['name']}, 描述:{extract_data['description']}\n"
    logging.info(result)
    return result
