#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/14 22:11
# Author:zhouxiaochuan
# Description:
from enum import IntEnum, Enum, StrEnum


class CsrdPubApiResultCode(IntEnum):
    SUCCESS = 200
    CAPTCHA_ERROR = 500  # 验证码错误会返回这个
    UNKNOWN = 201  # 未知错误我还不知道这个是什么意
    HANDLE_SUCCESS = 0  # 操作成功


CSRD_P_RESULT_CODES = [item.value for item in CsrdPubApiResultCode]


class CsrdPubApiStatus(StrEnum):
    SUCCESS = "1"
    ERROR = "0"
#
#
# class DmpOrganizationType(Enum):
#     TOP_DEPARTMENT = ("运维单位", "1")
#     COMPANY = ("集团公司", "2")
#     BUILDING_UNIT = ("建设单位", "3")
#     PROJECT = ("建设项目", "4")
#     SECTION = ("标段", "5")
#     BEAM = ("梁场", "6")
#
#     @property
#     def or_type(self):
#         return self.value[1]
#
#     @property
#     def name(self):
#         return self.value[0]
#
#
# DMP_ORGANIZATION_NAME = [item.name for item in DmpOrganizationType]
