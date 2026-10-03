#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 10:32
# Author:zhouxiaochuan
# Description:
import logging
from asyncio import log
from typing import Sequence

from langchain.tools import tool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.db.tables import ApiInfo, ApiTestCase


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
def get_api_summary():
    """
    获取所有接口的项目、模块、子模块、API名称
    Returns:
        所有接口的摘要列表
    """
    logging.info("获取所有接口摘要")
    result = "未找到指定的Api接口摘要。"
    with Session(db_engine) as session:
        stmt = select(ApiInfo.project_name, ApiInfo.module_name, ApiInfo.sub_module_name, ApiInfo.name)
        rows = session.execute(stmt).all()
        if rows:
            result = f"共{len(rows)}个Api接口摘要\n"
            for index, row in enumerate(rows):
                result += f"第{index + 1}个Api接口摘要: 项目={row.project_name}, 模块={row.module_name}, 子模块={row.sub_module_name}, API名称={row.name}\n"
    logging.info(result)
    return result


@tool
def save_test_case(key: str, title: str, description: str, module: str, sub_module: str) -> str:
    """
    保存测试用例到数据库
    Args:
        key: 用例的唯一标识
        title: 用例的名称
        description: 用例的详细描述
        module: 模块名称(中文)
        sub_module: 子模块名称(中文)

    Returns:
        保存结果
    """
    logging.info(f"保存测试用例: {key}, {title}, {description}, {module}, {sub_module}")
    try:
        with Session(db_engine) as session:
            session.add(
                ApiTestCase(
                    key=key,
                    title=title,
                    description=description,
                    module=module,
                    sub_module=sub_module
                ))
            session.commit()
    except IntegrityError as e:
        # 比如唯一约束冲突
        return f"保存失败：{key} 可能已存在。错误：{e}"
    except Exception as e:
        return f"保存失败：{e}"

    return f"成功保存测试用例: {key}, {title}, {description}, {module}, {sub_module}"
