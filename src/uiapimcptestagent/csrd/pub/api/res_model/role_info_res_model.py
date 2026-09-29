#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/16 11:20
# Author:zhouxiaochuan
# Description:
from typing import Optional

from pydantic import BaseModel, Field

from apl_clients.response_model import BaseBfmResponseModel

class RolePermissionResulItemtModel(BaseModel):
    """
    角色权限返回模型-角色权限结果
    """
    id: str
    roleName: str = Field(min_length=1)
    roleCode: str = Field(min_length=1)
    orgCategory: Optional[str] = Field(min_length=1)
    manageOrgCategory: Optional[str] = Field(pattern=r"^\d+(,\d+)*$")
    description: Optional[str]
    tenantId: Optional[str]
    createBy: Optional[str] = Field(min_length=1)
    createTime: str = Field( pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    updateBy: Optional[str] = Field(min_length=1)
    updateTime: Optional[str] = Field( pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


class RolePermissionResModel(BaseBfmResponseModel):
    """
    角色权限返回模型
    """
    result: Optional[list[RolePermissionResulItemtModel]]
