#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/21 10:26
# Author:zhouxiaochuan
# Description:

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from csrd.res_model.pub.base_csrd_response_model import BaseCsrdResponseModel
from uiapimcptestagent.tools.response_model_tool import api_res_model_register


class DeptNode(BaseModel):
    """部门树节点（递归结构）"""

    model_config = ConfigDict(extra="allow")  # 若想严格校验，可删掉此行或设为 "ignore"

    deptId: str = Field(..., description="部门ID")
    parentDept: Optional[str] = Field(None, description="父部门ID")
    deptName: str = Field(..., description="部门名称")
    deptType: Optional[str] = Field(None, description="部门类型")
    deptNo: Optional[str] = Field(None, description="部门编号")
    deptCode: Optional[str] = Field(None, description="部门编码")
    deptOrder: Optional[int] = Field(None, description="排序")
    deptRemark: Optional[str] = Field(None, description="备注")

    deptTypeName: Optional[str] = Field(None, description="部门类型名称")

    # 递归引用自身
    children: List["DeptNode"] = Field(default_factory=list, description="子部门列表")


# Pydantic v2 需要显式重建模型以解析前向引用
DeptNode.model_rebuild()

@api_res_model_register
class DeptResponse(BaseCsrdResponseModel):
    """接口响应包装"""

    data: List[DeptNode] = Field(default_factory=list, description="部门树数据")