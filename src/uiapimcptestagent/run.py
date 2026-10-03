#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/29 15:56
# Author:zhouxiaochuan
# Description:
# import os
# import subprocess

import pytest

from uiapimcptestagent.ai.agents.case_genrate_agent.chat_page import ChatPageThread


def run():
    pytest.main(['-vs', "./test/", "--alluredir=../allure-results", "--clean-alluredir"])

def demo():
    chart_page = ChatPageThread()
    chart_page.start()
    input("按任意键退出")
    chart_page.close()
    chart_page.join()


demo()