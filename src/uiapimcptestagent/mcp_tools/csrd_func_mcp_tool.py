#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/16 14:47
# Author:zhouxiaochuan
# Description:

from fastmcp.tools import tool

from uiapimcptestagent.apps import csrd_api_mcp
from uiapimcptestagent.csrd.tools.csrd_func_tool import CsrdFuncTool

public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoAWjg0r6UQ3fih4EZK8Sz4tIcRdM3LPFQEXwBJSKBsKiker89olABv7UM7NRQn0+OQ6Mz7gYbig+h1vK+RHtcwuJ/Ub7crz50NFuo+L+jxhR0mBNC0Sf9nAqUH/Q95715rRKiiwA5U5c9cF70ZCxFGcWZqJvQVUPiHVFwWbWZswIDAQAB
-----END PUBLIC KEY-----
"""



class CsrdFuncMcpTool:
    """
    Csrd功能助手类
    """
    @tool()
    def login_data_encrypt(self, username, password, captcha_code=None, captcha_request=None) -> str:
        """
        登陆信息加密
        Args:
            username: 用户名
            password: 密码
            captcha_code: 验证码
            captcha_request: 验证码请求参数

        Returns:

        """
        return CsrdFuncTool.login_data_encrypt(username, password, captcha_code, captcha_request)

csrd_func_tool = CsrdFuncMcpTool()
csrd_api_mcp.add_tool(csrd_func_tool.login_data_encrypt)
