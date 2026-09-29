#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 16:52
# Author:zhouxiaochuan
# Description:
import os

from uiapimcptestagent.api.clients.base_api_client_service import BaseAPiClientService


# from uiapimcptestagent.apps import csrd_api_mcp


def main():
    BaseAPiClientService().execute_test_case(single_api_test_case_key="user.login.success")
#     csrd_api_mcp.run(transport="http", host=os.getenv("IP"), port=int(os.getenv("PORT", 8099)))

