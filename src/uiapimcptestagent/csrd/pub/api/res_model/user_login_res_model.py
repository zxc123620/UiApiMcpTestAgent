#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/15 16:01
# Author:zhouxiaochuan
# Description:
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/15 16:01
# Author:zhouxiaochuan
# Description:
from typing import Optional, List

from pydantic import BaseModel

from uiapimcptestagent.csrd.pub.api.res_model.base_csrd_response_model import BaseCsrdResponseModel
from uiapimcptestagent.tools.response_model_tool import api_res_model_register


class UserParamModel(BaseModel):
    """
    用户参数模型
    """
    loginTip: Optional[str]
    userAdmin: Optional[str]
    roleIdStr: Optional[str]
    roleNameStr: Optional[str]
    permissionStr: Optional[str]
    permissionSet: Optional[List[str]]


class SystemParamModel(BaseModel):
    """
    系统参数模型
    """
    logoutUrl: Optional[str]
    websocketOnline: Optional[str]
    rabbitmqHost: Optional[str]
    rabbitmqUsername: Optional[str]
    rabbitmqPassword: Optional[str]
    rabbitmqPort: Optional[str]


class LoginDataModel(BaseModel):
    """
    登录返回数据模型
    """
    userId: str
    userNo: Optional[str]
    userJob: Optional[str]
    userName: str
    userPassword: Optional[str]
    userPasswordSalt: Optional[str]
    userMobile: Optional[str]
    userEmail: Optional[str]
    userSex: Optional[str]
    userLocked: Optional[str]
    loginCount: Optional[int]
    loginTime: Optional[str]
    loginIp: Optional[str]
    userAccount: Optional[str]
    userProtect: Optional[str]
    userPasswordPolicy: Optional[str]
    userPasswordDate: Optional[str]
    userWhiteIp: Optional[str]
    userPeriod: Optional[str]
    deptId: Optional[str]
    userAdmin: Optional[str]
    userFlag: Optional[str]
    createUser: Optional[str]
    createTime: Optional[str]
    updateUser: Optional[str]
    updateTime: Optional[str]
    userParam: Optional[UserParamModel]
    systemParam: Optional[SystemParamModel]
    userSexName: Optional[str]
    userFlagName: Optional[str]
    userPasswordPolicyName: Optional[str]
    userPasswordOld: Optional[str]
    confirmPassword: Optional[str]
    userPasswordStatus: Optional[str]
    userOnline: Optional[bool]
    onlineCount: Optional[int]
    scopeTypeStr: Optional[str]
    scopeSql: Optional[str]
    roleId: Optional[str]
    roleIdStr: Optional[str]
    roleNameStr: Optional[str]
    permissionStr: Optional[str]
    permissionSet: Optional[List[str]]
    mapIdStr: Optional[str]
    userAuthStr: Optional[str]
    captchaRequest: Optional[str]
    captchaCode: Optional[str]
    userToken: Optional[str]
    jwtToken: Optional[str]
    showAdmin: Optional[str]

@api_res_model_register
class UserLoginResModel(BaseCsrdResponseModel):
    """
    用户登录返回模型
    """
    data: Optional[LoginDataModel]