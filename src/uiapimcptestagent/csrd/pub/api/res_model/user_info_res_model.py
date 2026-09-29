from typing import List, Optional, Any
from pydantic import BaseModel

from uiapimcptestagent.csrd.dmp.api import BaseCsrdResponseModel, CsrdPageData


class CsrdUserInfo(BaseModel):
    userId: str
    userNo: str
    userJob: str
    userName: str
    userPassword: Optional[Any] = None
    userPasswordSalt: Optional[Any] = None
    userMobile: str
    userEmail: str
    userSex: str
    userLocked: str
    loginCount: int
    loginTime: str
    loginIp: str
    userAccount: str
    userProtect: str
    userPasswordPolicy: str
    userPasswordDate: Optional[Any] = None
    userWhiteIp: str
    userPeriod: Optional[Any] = None
    deptId: str
    userAdmin: str
    userFlag: str
    createUser: Optional[Any] = None
    createTime: Optional[Any] = None
    updateUser: Optional[Any] = None
    updateTime: Optional[Any] = None
    userParam: Optional[Any] = None
    systemParam: Optional[Any] = None
    userSexName: str
    userFlagName: str
    userPasswordPolicyName: Optional[Any] = None
    userPasswordOld: Optional[Any] = None
    confirmPassword: Optional[Any] = None
    userPasswordStatus: Optional[Any] = None
    userOnline: bool
    onlineCount: int
    scopeTypeStr: Optional[Any] = None
    scopeSql: Optional[Any] = None
    roleId: Optional[Any] = None
    roleIdStr: Optional[str] = None
    roleNameStr: Optional[str] = None
    permissionStr: Optional[Any] = None
    permissionSet: Optional[Any] = None
    mapIdStr: Optional[Any] = None
    userAuthStr: Optional[str] = None
    captchaRequest: Optional[Any] = None
    captchaCode: Optional[Any] = None
    userToken: Optional[Any] = None
    jwtToken: Optional[Any] = None
    showAdmin: Optional[Any] = None


class CsrdUserPageData(CsrdPageData):
    list: List[CsrdUserInfo]


class CsrdUserInfoResponse(BaseCsrdResponseModel):
    data: Optional[CsrdUserPageData] = None
