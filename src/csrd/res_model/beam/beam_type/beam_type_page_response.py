#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/29 17:21
# Author:zhouxiaochuan
# Description:
from typing import List, Optional
from pydantic import BaseModel, Field

from csrd.res_model.pub.base_csrd_response_model import BaseCsrdResponseModel, CsrdPageData
from uiapimcptestagent.tools.response_model_tool import api_res_model_register

class BeamTypeItem(BaseModel):
    btId: str = Field(..., description="主键")
    name: str = Field(..., description="梁型名称")
    beamBodyType: str = Field(..., description="梁体类型（1T梁；2箱梁）")
    beamLengthType: str = Field(..., description="长度类型(1、32米；2、 24米；3、20米；4、16米；5、40米；6、其他 )")
    beamLength: float = Field(..., description="跨度，单位M，保留小数点后三位")
    sjth: str = Field(..., description="通图号")
    barrierType: str = Field(..., description="声屏障(0无声；1有声)")
    lineType: str = Field(..., description="正线类型（1单线；2双线）")
    zpType: str = Field(..., description="线型（1直线；2曲线）")
    beamLocation: Optional[str] = Field(default=None, description="T型梁位置(1中梁；2边梁；3次边梁)")
    planTotal: int = Field(..., description="计划生产数量")
    beamTypeColor: Optional[str] = Field(default=None, description="架梁图例颜色")


class PageData(CsrdPageData):
    list: Optional[List[BeamTypeItem]] = Field(default=None, description="梁型列表")


@api_res_model_register
class BeamTypePageResponse(BaseCsrdResponseModel):
    """
    梁型分页响应模型
    """
    status: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    timestamp: Optional[int] = Field(default=None)
    data: Optional[PageData] = Field(default=None)