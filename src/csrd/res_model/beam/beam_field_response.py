#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/25 22:09
# Author:zhouxiaochuan
# Description:
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from csrd.res_model.pub.base_csrd_response_model import BaseCsrdResponseModel
from uiapimcptestagent.tools.response_model_tool import api_res_model_register


class BeamFieldData(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    # --- 必须字段 ---
    bf_id: str = Field(..., alias="bfId", description="梁场id;queryParamEq")
    project_name: str = Field(..., alias="projectName", description="项目名称")
    project_short_name: str = Field(..., alias="projectShortName", description="项目简称")
    start_city: str = Field(..., alias="startCity", description="起点端城市")
    end_city: str = Field(..., alias="endCity", description="终点端城市")
    part_name: str = Field(..., alias="partName", description="标段名称")
    con_unit_name: str = Field(..., alias="conUnitName", description="施工单位名称")
    sup_unit_name: str = Field(..., alias="supUnitName", description="监理单位名称")
    beam_field_name: str = Field(..., alias="beamFieldName", description="梁场名称(梁场简称)")
    address: str = Field(..., description="梁场所在地址")
    leader_name: str = Field(..., alias="leaderName", description="梁场场长")
    leader_phone: str = Field(..., alias="leaderPhone", description="梁场场长手机号")
    eng_name: str = Field(..., alias="engName", description="梁场总工")
    line_mileage_name: str = Field(..., alias="lineMileageName", description="所在正线里程冠号")
    line_mileage: str = Field(..., alias="lineMileage", description="所在正线里程")
    beam_type: str = Field(..., alias="beamType", description="生产梁型：1、T梁2、箱梁3、混合梁")
    max_product_num: int = Field(..., alias="maxProductNum", description="日最大生产能力（榀）")
    product_count_t: int = Field(..., alias="productCountT", description="t梁设计量")
    product_count_x: int = Field(..., alias="productCountX", description="箱梁设计量")
    product_count: int = Field(..., alias="productCount", description="总设计量")
    lab_name: str = Field(..., alias="labName", description="试验室名称")
    lab_director: str = Field(..., alias="labDirector", description="试验室负责人姓名")
    lab_director_phone: str = Field(..., alias="labDirectorPhone", description="试验室负责人手机号码")
    mix_station: str = Field(..., alias="mixStation", description="拌和站名称")
    bridge_introduction: str = Field(..., alias="bridgeIntroduction", description="梁场简介")
    set_up_type: str = Field(..., alias="setUpType", description="架梁方式：0跨线提梁上桥、1正线运梁上桥")

    # --- 非必须字段 ---
    eng_phone: Optional[str] = Field(None, alias="engPhone", description="总工手机号")
    three_check_name: Optional[str] = Field(None, alias="threeCheckName", description="第三方检测单位名称")
    certification_date: Optional[str] = Field(None, alias="certificationDate", description="梁场认证日期")
    area: Optional[float] = Field(None, description="梁场占地面积（亩）") # 原定义是 number，对应 float
    plan_start_date: Optional[str] = Field(None, alias="planStartDate", description="计划开工日期")
    plan_end_date: Optional[str] = Field(None, alias="planEndDate", description="计划完工日期")
    plan_put_up_start_date: Optional[str] = Field(None, alias="planPutUpStartDate", description="计划架梁开始日期")
    plan_put_up_end_date: Optional[str] = Field(None, alias="planPutUpEndDate", description="计划架梁结束日期")
    first_put_up_start_kilo: Optional[float] = Field(None, alias="firstPutUpStartKilo", description="首架梁小里程墩身里程值（米）")
    first_put_up_end_kilo: Optional[float] = Field(None, alias="firstPutUpEndKilo", description="首架梁大里程墩身里程值（米）")
    location_id: Optional[str] = Field(None, alias="locationId", description="气象数据行政位置id")
    three_dimensional: Optional[str] = Field(None, alias="threeDimensional", description="三维大屏地址")
    two_dimensional: Optional[str] = Field(None, alias="twoDimensional", description="二维大屏地址")
    wx_back_url: Optional[str] = Field(None, alias="wxBackUrl", description="微信轮播地址")
    electronic_sign_id: Optional[str] = Field(None, alias="electronicSignId", description="电子标识牌id")
    set_up_location_type: Optional[str] = Field(None, alias="setUpLocationType", description="梁场位置：0线路右侧、1线路左侧")
    tenant_id: Optional[str] = Field(None, alias="tenantId", description="租户标识")
    create_by: Optional[str] = Field(None, alias="createBy", description="创建人")
    create_time: Optional[str] = Field(None, alias="createTime", description="创建日期")
    update_by: Optional[str] = Field(None, alias="updateBy", description="修改人")
    update_time: Optional[str] = Field(None, alias="updateTime", description="修改日期")

@api_res_model_register
class BeamFieldResponse(BaseCsrdResponseModel):
    """最外层响应结构"""
    data: list[BeamFieldData] = Field(..., description="梁场核心数据")
