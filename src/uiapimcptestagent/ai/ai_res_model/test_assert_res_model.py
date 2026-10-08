#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/7 12:38
# Author:zhouxiaochuan
# Description:
from pydantic import BaseModel, Field


class ApiTestAssertResModel(BaseModel):
    pass_: bool=Field(description="是否通过")
    reason: str = Field(description="失败的原因")
