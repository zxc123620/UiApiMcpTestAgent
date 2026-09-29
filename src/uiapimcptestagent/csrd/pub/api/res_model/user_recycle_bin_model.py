#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/16 13:22
# Author:zhouxiaochuan
# Description:
from typing import Optional, Union

from pydantic import BaseModel

from apl_clients.response_model import BaseBfmResponseModel


class RecycleBinUserInfoResultItemModel(BaseModel):
    """
    回收站用户信息返回模型-回收站用户信息结果
    """
    id: str
    username: str
    tkusername: Optional[str]
    realname: Optional[str]
    avatar: Optional[str]
    birthday: Optional[str]
    sex: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    orgCode: Optional[Union[int, str]]
    orgCodeTxt: Optional[str]
    status: int
    delFlag: int
    workNo: Optional[str]
    post: Optional[str]
    telephone: Optional[str]
    beamFieldId: Optional[str]
    createBy: Optional[str]
    createTime: Optional[str]
    updateBy: Optional[str]
    updateTime: Optional[str]
    activitiSync: Optional[int]
    userIdentity: Optional[int]
    departIds: Optional[str]
    thirdType: Optional[str]
    relTenantIds: Optional[str]
    clientId: Optional[str]
    rootTenantId: Optional[str]
    remarks: Optional[str]
    projectList: Optional[list[str]]
    companyType: Optional[str]
    orgCategory: Optional[str]
    orgType: Optional[str]
    tenantName: Optional[str]


class RecycleBinUserInfoResModel(BaseBfmResponseModel):
    """
    回收站用户信息返回模型
    """
    result: Optional[list[RecycleBinUserInfoResultItemModel]]
