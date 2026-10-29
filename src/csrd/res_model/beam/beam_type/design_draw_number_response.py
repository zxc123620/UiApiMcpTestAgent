#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/29 17:19
# Author:zhouxiaochuan
# Description:
from typing import List, Optional
from pydantic import BaseModel, Field

from csrd.res_model.pub.base_csrd_response_model import BaseCsrdResponseModel
from uiapimcptestagent.tools.response_model_tool import api_res_model_register


class BddItem(BaseModel):
    bddId: Optional[str] = Field(default=None, description="主键;queryParamEq")
    designDrawingsNumber: str = Field(..., description="图号")
    designBeamType: str = Field(..., description="梁型码")
    bddSort: Optional[str] = Field(default=None, description="序号")
    numberType: Optional[str] = Field(default=None, description="1.基础编码2.其他编码")

@api_res_model_register
class DesignDrawNumberRes(BaseCsrdResponseModel):
    """
    设计图号响应模型
    """
    data: Optional[List[BddItem]] = Field(default=None, description="数据列表")