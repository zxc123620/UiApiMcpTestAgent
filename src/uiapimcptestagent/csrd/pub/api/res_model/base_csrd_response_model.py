#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/15 15:55
# Author:zhouxiaochuan
# Description:
import logging
from typing import Union, List
from pydantic import field_validator

from typing import Optional

from pydantic import BaseModel, model_validator

from uiapimcptestagent.csrd.pub.api.pub_res_code import CSRD_P_RESULT_CODES


class BaseCsrdResponseModel(BaseModel):
    """
    用户基础返回模型
    """
    code: int
    data: Optional[Union[dict, list, bool, str]]
    message: Optional[str] = None
    status: str
    timestamp: int

    @field_validator("code")
    @classmethod
    def validate_code(cls, code: int):
        if code in CSRD_P_RESULT_CODES:
            return code
        raise ValueError(f"不支持的业务状态码: {code}")



class CsrdPageData(BaseModel):
    """
    分页数据模型
    """
    total: int
    pageNum: int
    pageSize: int
    size: int
    startRow: int
    endRow: int
    pages: int
    prePage: int
    nextPage: int
    isFirstPage: bool
    isLastPage: bool
    hasPreviousPage: bool
    hasNextPage: bool
    navigatePages: int
    navigatepageNums: list[int] = []
    navigateFirstPage: int
    navigateLastPage: int

    @model_validator(mode="after")
    def valid_total_and_list(self):
        """
        验证total数量 与 list、pages、size 关系对不对
        :return:
        """
        # 验证 endRow 是否等于 size
        # assert self.endRow == self.size
        if self.list:
            # list数量 验证 不为0
            logging.info(f"list数量: {len(self.list)} 开始验证")
            data_len = len(self.list)
            # 验证 pages 是否小于 navigatepageNums[-1]
            # assert self.pages <= self.navigatepageNums[-1], f"pages({self.pages})大于navigatepageNums[-1]({self.navigatepageNums[-1]})" 用不了,只能到8 ，从9开始才能往后
            # 验证 data_len 数量小于 total
            assert data_len <= self.total, f"data_len({data_len})大于total({self.total})"
            # 验证 data_len 数量等于 size
            assert data_len == self.size, f"data_len({data_len})不等于size({self.size})"
            # 验证total数量
            assert self.total <= self.pages * self.pageSize, f"total({self.total})大于pages({self.pages})*size({self.size})"
            # 验证 prePage 是否等于 0 或者 pages - 1
            assert self.prePage == 0 or self.prePage == self.pageNum - 1, f"prePage({self.prePage})不等于0或pageNum({self.pageNum})-1"
            # 验证 navigateFirstPage 是否等于 1
            # assert self.navigateFirstPage == 1, f"navigateFirstPage({self.navigateFirstPage})不等于1" 用不了,只能到8 ，从9开始才能往后
            # 验证 navigateLastPage 是否等于 navigatepageNums[-1]
            # assert self.navigateLastPage == self.navigatepageNums[-1], f"navigateLastPage({self.navigateLastPage})不等于navigatepageNums[-1]({self.navigatepageNums[-1]})" 用不了,只能到8 ，从9开始才能往后
            #  验证 是否存在下一页
            if self.pageNum < self.navigatepageNums[-1]:
                assert self.hasNextPage == True, f"hasNextPage({self.hasNextPage})不等于True"
            else:
                assert self.hasNextPage == False, f"hasNextPage({self.hasNextPage})不等于False"
            # 验证 存在下一页 且不是最后一页
            if self.pageNum == self.navigatepageNums[-1]:
                assert self.isLastPage == True, f"isLastPage({self.isLastPage})不等于True"
                assert self.nextPage == 0, f"nextPage({self.nextPage})不等于0"
            else:
                assert self.isLastPage == False, f"isLastPage({self.isLastPage})不等于False"
                # assert self.nextPage == self.navigatepageNums[self.pageNum + 1], f"nextPage({self.nextPage})不等于navigatepageNums[self.pageNum + 1]({self.navigatepageNums[self.pageNum + 1]})" 用不了,只能到8 ，从9开始才能往后
            # 验证 存在上一页 且不是第一页
            if self.pageNum == 1:
                assert self.hasPreviousPage == False, f"hasPreviousPage({self.hasPreviousPage})不等于False"
                assert self.isFirstPage == True, f"isFirstPage({self.isFirstPage})不等于True"
            else:
                assert self.hasPreviousPage == True, f"hasPreviousPage({self.hasPreviousPage})不等于True"
                assert self.isFirstPage == False, f"isFirstPage({self.isFirstPage})不等于False"
        else:
            # list数量为0 验证
            assert self.pages == 0, f"pages({self.pages})不等于0"
            assert self.prePage == 0, f"prePage({self.prePage})不等于0"
            assert self.nextPage == 0, f"nextPage({self.nextPage})不等于0"
            assert self.isFirstPage == True, f"isFirstPage({self.isFirstPage})不等于True"
            assert self.isLastPage == True, f"isLastPage({self.isLastPage})不等于True"
            assert self.navigateFirstPage == 0, f"navigateFirstPage({self.navigateFirstPage})不等于0"
            assert self.navigateLastPage == 0, f"navigateLastPage({self.navigateLastPage})不等于0"
            assert self.navigatepageNums == [],  f"navigatepageNums({self.navigatepageNums})不等于[]"
            assert self.hasNextPage == False, f"hasNextPage({self.hasNextPage})不等于False"
            assert self.hasPreviousPage == False, f"hasPreviousPage({self.hasPreviousPage})不等于False"
            assert self.startRow == 0, f"startRow({self.startRow})不等于0"
            assert self.endRow == 0, f"endRow({self.endRow})不等于0"

        return self

