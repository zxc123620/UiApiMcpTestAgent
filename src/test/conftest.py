#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/16 17:03
# Author:zhouxiaochuan
# Description:
import os

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/30 14:48
# Author:zhouxiaochuan
# Description:
from sqlalchemy import select
from sqlalchemy.orm import Session

from uiapimcptestagent import db_engine
from uiapimcptestagent.db.tables import ApiTestCase

import dotenv
dotenv.load_dotenv()

def pytest_addoption(parser):
    """
    添加自定义命令行参数
    Args:
        parser:

    Returns:

    """
    parser.addoption("--module", action="store", required=False,default="all", help="测试用例模块")
    parser.addoption("--sub_module", action="store", required=False,default="all", help="测试用例子模块")
    parser.addoption("--title", action="store", required=False,default="all", help="测试用例标题")


def pytest_generate_tests(metafunc):
    """
    生成测试用例
    Args:
        metafunc:

    Returns:

    """
    module_str = metafunc.config.getoption("module")
    sub_module_str = metafunc.config.getoption("sub_module")
    print("模块=", module_str)
    print("子模块=", sub_module_str)

    module_list = module_str.split(" ")
    module_list = [ module.replace(' ', '') for module in module_list if str(module).replace(' ', '') != ""]
    sub_module_list = sub_module_str.split(" ")
    title = metafunc.config.getoption("title")
    # 登录用例key
    login_case_key= os.getenv("login_case_key", None)
    if login_case_key is not None:
        case_ids = [login_case_key]
    with Session(db_engine) as session:
        # 获取测试用例
        stmt = select(ApiTestCase).where(ApiTestCase.is_active == True)
        if module_str != "all":
            stmt = stmt.where(ApiTestCase.module_name.in_(module_list))
        if sub_module_str != "all":
            stmt = stmt.where(ApiTestCase.sub_module_name.in_(sub_module_list))
        if title != "all":
            stmt = stmt.where(ApiTestCase.title.like(f"%{title}%"))
        api_test_cases = session.scalars(stmt).all()
        case_ids = [ api_test_case.key for api_test_case in api_test_cases]
    # 添加测试用例参数化
    if "case_id" in metafunc.fixturenames:
        # 将一个函数扩展成多个用例节点
        metafunc.parametrize("case_id", case_ids,indirect=True)
