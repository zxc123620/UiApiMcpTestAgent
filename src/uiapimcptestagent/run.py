#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/29 15:56
# Author:zhouxiaochuan
# Description:
# import os
# import subprocess

import pytest

def run():
    pytest.main(['-vs', "./test/", "--alluredir=../allure-results", "--clean-alluredir"])

run()