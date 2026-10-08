#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 22:18
# Author:zhouxiaochuan
# Description:
from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor


@StringMethodExecutor.register("method")
def method(a,b,c):
    """
    方法描述
    用于打印参数a、b、c的值
    Args:
        a: 参数a的值
        b: 参数b的值
        c: 参数c的值

    Returns:

    """
    print(a)
    print(b)
    print(c)


print(StringMethodExecutor.get_func_doc())
