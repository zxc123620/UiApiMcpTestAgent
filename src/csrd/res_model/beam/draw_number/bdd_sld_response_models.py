# -*- coding: utf-8 -*-
"""
梁体通图号 / 静载试验设计参数 —— 查询类接口的响应模型（Pydantic V2）

依据文档：
  · 桥梁与载荷计算/梁体与通图号.md
  · 桥梁与载荷计算/桥梁设计与载荷计算.md

覆盖的 6 个查询接口（均为 GET，返回统一外壳 status/code/message/timestamp/data）：

┌──────────────────────────────────────────────┬──────────────────────────────┬──────────────────────────┐
│ 接口                                          │ Path                          │ 响应模型                  │
├──────────────────────────────────────────────┼──────────────────────────────┼──────────────────────────┤
│ 通图号-分页列表查询                            │ .../queryBfmBaseDesignDrawingsNumberVoPage │ BddPageResponse          │
│ 通图号-列表查询                                │ .../queryBfmBaseDesignDrawingsNumberVoList │ BddListResponse          │
│ 通图号-通过 id 查询                            │ .../queryBfmBaseDesignDrawingsNumberById   │ BddDetailResponse        │
│ 静载参数-分页列表查询                          │ .../queryBfmBaseStaticloadDesignVoPage     │ StaticLoadPageResponse   │
│ 静载参数-列表查询                              │ .../queryBfmBaseStaticloadDesignVoList     │ StaticLoadListResponse   │
│ 静载参数-通过 id 查询                          │ .../queryBfmBaseStaticloadDesignById       │ StaticLoadDetailResponse │
└──────────────────────────────────────────────┴──────────────────────────────┴──────────────────────────┘

使用示例：
    from bdd_sld_response_models import BddPageResponse

    resp = requests.get(url, params={"pageNum": 1, "pageSize": 10}, headers=headers)
    page = BddPageResponse.model_validate(resp.json())      # 解析失败会抛 ValidationError，本身就是一条断言
    assert page.code == "200"
    assert page.data is not None and page.data.total >= 1
    for row in page.data.list:
        print(row.bdd_id, row.design_drawings_number, row.number_type)

设计约定：
1. **字段名用 snake_case，`alias` 对应接口的驼峰键**（如 `bdd_id` ↔ `bddId`）。
   配置了 `populate_by_name=True`，所以 `alias` 和字段名两种写法都能用于解析；
   需要还原成接口原始 JSON 时用 `model_dump(by_alias=True)`。
2. **全部字段可空**：文档里多数字段标「非必须」，且列表为空、分页无上下页时后端会返回 null，
   因此数值/字符串一律 Optional；缺字段也不会报错（`extra="allow"`，多出来的字段
   ——例如后端补充的 createTime / deptId——会被保留而不是丢弃或报错）。
3. **数值宽松解析**：后端可能把数字返回成字符串（`"50"`）或空串（`""`），
   统一用 `BeforeValidator` 把空串归一化为 None，再由 pydantic 的 lax 模式转成 float/int。
4. **枚举值用 Enum 表达**，同时允许数字型枚举（`1` 会被转成 `"1"`）——
   文档标注这些字段是 string，但实际返回数字时不应该因为类型细节让断言失败。
5. 文档未列、但业务上确定存在的字段（如通图号列表里新建记录排第一所依赖的排序字段），
   一律加注释说明「文档未列」，不臆造必填。

作者备注：本文件只是「响应解析/断言用的数据契约」，不含请求参数模型；
请求参数（分页、过滤条件）见上面两份文档的「请求参数」表。
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from csrd.res_model.pub.base_csrd_response_model import ApiModel, CsrdPageResult, BaseCsrdApiResponse
from uiapimcptestagent.api.base_api_client import ApiResponse

T = TypeVar("T")


# ======================================================================================
# 通用解析工具
# ======================================================================================
def _blank_to_none(value: Any) -> Any:
    """把「空字符串 / 纯空白字符串」归一化为 None。

    后端在字段未配置时经常返回 `""` 而不是 `null`，直接交给 float/int 转换会抛
    ValidationError；这类「没填」在业务上等同于 null，故统一在 before 阶段抹平。
    """
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _coerce_strlike(value: Any) -> Any:
    """把「字符串型字段」的取值统一成 str（数字会被转成字符串），空串归一化为 None。

    用于 code / status / 枚举值等：文档标注 string，但后端返回数字（`code: 200`、
    `numberType: 1`）时不应该报类型错误。布尔值不走数字分支，避免 True → "True"。
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        # 1.0 这种整数值转成 "1"，避免出现 "1.0" 这种非预期的枚举字面量
        return str(int(value)) if float(value).is_integer() else str(value)
    if isinstance(value, str):
        return value.strip() or None
    return value


# 常用字段类型别名：可空 + 空串归一化
OptFloat = Annotated[Optional[float], BeforeValidator(_blank_to_none)]
OptInt = Annotated[Optional[int], BeforeValidator(_blank_to_none)]
OptStr = Annotated[Optional[str], BeforeValidator(_coerce_strlike)]
OptBool = Annotated[Optional[bool], BeforeValidator(_blank_to_none)]




# ======================================================================================
# 一、统一响应外壳
# ======================================================================================
# class ApiResponse(ApiModel, Generic[T]):
#     """所有接口共用的响应外壳。
#
#     形如：{"status": "1", "code": "200", "message": "操作成功", "timestamp": 1730000000000, "data": ...}
#     """
#
#     status: OptStr = Field(
#         default=None,
#         description="业务状态标识，与 code 配合判断成功与否；具体取值以后端约定为准",
#     )
#     code: OptStr = Field(
#         default=None,
#         description="状态码，字符串形式（如 \"200\"）；后端返回数字时会被自动转成字符串",
#     )
#     message: OptStr = Field(default=None, description="提示信息，失败时通常带具体原因")
#     timestamp: OptInt = Field(default=None, description="服务端时间戳（毫秒）")
#     data: Optional[T] = Field(
#         default=None,
#         description="业务数据；本文件的泛型参数决定其具体结构（对象 / 数组 / 分页对象）",
#     )


# class PageResult(_ApiModel, Generic[T]):
#     """分页查询的 `data` 结构（PageHelper 风格）。
#
#     注意：列表为空或只有一页时，`pre_page` / `next_page` 等字段常常是 null，
#     所以全部可空；`navigatepage_nums`（文档原样拼写，注意是小写 p）是页码导航数组。
#     """
#
#     total: OptInt = Field(default=None, description="总记录数")
#     list: List[T] = Field(
#         default_factory=list,
#         description="当前页数据；字段名与接口一致就叫 list，缺省时为空数组而不是 None",
#     )
#     page_num: OptInt = Field(default=None, alias="pageNum", description="当前页码（从 1 开始）")
#     page_size: OptInt = Field(default=None, alias="pageSize", description="每页条数")
#     size: OptInt = Field(default=None, description="当前页实际条数")
#     start_row: OptInt = Field(default=None, alias="startRow", description="当前页起始行号")
#     end_row: OptInt = Field(default=None, alias="endRow", description="当前页结束行号")
#     pages: OptInt = Field(default=None, description="总页数")
#     pre_page: OptInt = Field(default=None, alias="prePage", description="上一页页码；首页时为 0 或 null")
#     next_page: OptInt = Field(default=None, alias="nextPage", description="下一页页码；末页时为 0 或 null")
#     is_first_page: OptBool = Field(default=None, alias="isFirstPage", description="是否首页")
#     is_last_page: OptBool = Field(default=None, alias="isLastPage", description="是否末页")
#     has_previous_page: OptBool = Field(default=None, alias="hasPreviousPage", description="是否有上一页")
#     has_next_page: OptBool = Field(default=None, alias="hasNextPage", description="是否有下一页")
#     navigate_pages: OptInt = Field(default=None, alias="navigatePages", description="导航页码数量")
#     navigatepage_nums: Optional[List[int]] = Field(
#         default=None,
#         alias="navigatepageNums",
#         description="导航页码数组（文档原样拼写，注意不是 navigatePageNums）",
#     )
#     navigate_first_page: OptInt = Field(default=None, alias="navigateFirstPage", description="导航首页码")
#     navigate_last_page: OptInt = Field(default=None, alias="navigateLastPage", description="导航末页码")


# ======================================================================================
# 二、梁体通图号（bfmBaseDesignDrawingsNumber）
# ======================================================================================
class NumberType(str, Enum):
    """编码类型（通图号 numberType）。

    · BASIC = "1"：基础编码，由「初始化通图号」接口批量生成（共 153 条），**不可编辑、不可删除**
    · OTHER = "2"：用户在页面上新增的编码，可编辑、可删除

    该字段只在**查询接口**返回；新增/编辑入参不带它（新增必然是 2）。
    """

    BASIC = "1"
    OTHER = "2"


class DesignDrawingsNumberItem(ApiModel):
    """通图号列表 / 分页列表中的一行（`data.list[*]`）。"""

    bdd_id: OptStr = Field(
        default=None,
        alias="bddId",
        description="主键。新增接口不返回主键，需要靠列表按梁型码回查拿到它",
    )
    design_drawings_number: OptStr = Field(
        default=None,
        alias="designDrawingsNumber",
        description="图号名称（业务上必填，长度 1~50；文档标「必须」但查询返回时仍按可空处理以防脏数据）",
    )
    design_beam_type: OptStr = Field(
        default=None,
        alias="designBeamType",
        description="梁型码（3 位数字字符串，仅允许 153~998；001~152 与 999 被国铁内置编码占用）",
    )
    bdd_sort: OptInt = Field(
        default=None,
        alias="bddSort",
        description="序号，越小越靠前。文档标注类型为 string，此处按序号语义用 int（"
        "传 \"10\" 也能解析）；新建记录默认排在最前即依赖该值或创建时间倒序",
    )
    number_type: Annotated[Optional[NumberType], BeforeValidator(_coerce_strlike)] = Field(
        default=None,
        alias="numberType",
        description="编码类型：1=基础编码（初始化生成，不可改删）、2=其他编码（用户新增）",
    )


class DesignDrawingsNumberDetail(ApiModel):
    """通图号「通过 id 查询」的 `data` 结构。

    与列表行的差异：文档未列 `bddSort`（本模型保留为可空字段，兼容实际返回）；
    其余字段一致。因为配置了 `extra="allow"`，文档没写的字段也不会丢。
    """

    bdd_id: OptStr = Field(default=None, alias="bddId", description="主键")
    design_drawings_number: OptStr = Field(
        default=None, alias="designDrawingsNumber", description="图号名称"
    )
    design_beam_type: OptStr = Field(
        default=None, alias="designBeamType", description="梁型码（3 位，153~998）"
    )
    number_type: Annotated[Optional[NumberType], BeforeValidator(_coerce_strlike)] = Field(
        default=None, alias="numberType", description="编码类型：1=基础编码、2=其他编码"
    )
    bdd_sort: OptInt = Field(
        default=None, alias="bddSort", description="序号（文档未列，实际可能返回；保留以便断言排序）"
    )


class BddPageResponse(BaseCsrdApiResponse[CsrdPageResult[DesignDrawingsNumberItem]]):
    """通图号-分页列表查询的完整响应。

    GET /base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoPage.ajax
    请求参数（Query）：bddId / designDrawingsNumber / designBeamType / bddSort / numberType，
    分页参数用 pageNum、pageSize。

    典型断言：
        page = BddPageResponse.model_validate(resp.json())
        assert page.data.list[0].design_drawings_number == "测试通图号-...";  # 新建排最前
    """


class BddListResponse(BaseCsrdApiResponse[List[DesignDrawingsNumberItem]]):
    """通图号-列表查询的完整响应（`data` 直接是数组，没有 total/分页字段）。

    GET /base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoList.ajax
    该接口同时被梁型管理模块用作「取通图号列表拿 bddId」的数据源。
    """


class BddDetailResponse(BaseCsrdApiResponse[DesignDrawingsNumberDetail]):
    """通图号-通过 id 查询的完整响应（`data` 是单个对象）。

    GET /base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberById.ajax
    请求参数（Query）：bddId（必填）。
    """


# ======================================================================================
# 三、静载试验设计参数（bfmBaseStaticloadDesign）
# ======================================================================================
class PsType(str, Enum):
    """预应力类型（`psType`）。"""

    FULL_PRESTRESS = "1"  # 全预应力梁
    LIMITED_TENSION = "2"  # 允许出现有限拉应力 / 允许出现裂缝但裂缝宽度受限的预应力梁


class LoadType(str, Enum):
    """荷载类型（`loadType`）。"""

    ZHONG_HUOZAI = "0"  # 中-活载
    ZK_HUOZAI = "1"  # ZK 活载


class StaticLoadDesignItem(ApiModel):
    """静载试验设计参数列表 / 分页列表中的一行（`data.list[*]`）。

    一个通图号（bddId）对应唯一一条静载参数（1:1）；`btdId` 是服务端生成的主键，
    新增接口不返回它，需要按 bddId 回查获取。
    字段分三组：关联与必填项（bddId/rd/ed/fl）、枚举项（psType/loadType）、其余为可选计算参数。
    """

    # ---- 关联与主键
    btd_id: OptStr = Field(default=None, alias="btdId", description="主键（服务端生成，新增不返回）")
    bdd_id: OptStr = Field(default=None, alias="bddId", description="所属通图号 id（关联 bfmBaseDesignDrawingsNumber.bddId）")

    # ---- 必填设计参数
    rd: OptFloat = Field(default=None, description="设计混凝土强度 Rd（MPa）")
    ed: OptFloat = Field(default=None, description="设计混凝土弹性模量 Ed（GPa）")
    fl: OptStr = Field(default=None, description="设计挠跨比 f/L，形如 \"1/800\"（是比值文本，不是数值）")

    # ---- 枚举项
    ps_type: Annotated[Optional[PsType], BeforeValidator(_coerce_strlike)] = Field(
        default=None,
        alias="psType",
        description="预应力类型：1=全预应力梁、2=允许有限拉应力/裂缝宽度受限",
    )
    load_type: Annotated[Optional[LoadType], BeforeValidator(_coerce_strlike)] = Field(
        default=None,
        alias="loadType",
        description="荷载类型：0=中-活载、1=ZK 活载",
    )

    # ---- 截面 / 抗力类参数
    kf: OptFloat = Field(default=None, description="抗裂安全系数 Kf")
    w0: OptFloat = Field(default=None, description="对跨中截面下边缘换算截面抵抗矩 W0")
    a0: OptFloat = Field(default=None, description="中跨截面换算截面面积 A0")
    e0: OptFloat = Field(default=None, description="中跨截面预应力合力中心至换算截面重心的距离 e0")
    ay: OptFloat = Field(default=None, description="中跨截面预应力钢束面积 Ay")
    ag: OptFloat = Field(default=None, description="中跨截面普通钢筋截面面积 Ag")

    # ---- 挠度 / 弯矩类参数
    fpsi: OptFloat = Field(default=None, description="实测挠度修正系数 ψ")
    md: OptFloat = Field(default=None, description="二期恒载质量对跨中弯矩 Md")
    mf: OptFloat = Field(default=None, description="防水层质量对跨中弯矩 Mf")
    mh: OptFloat = Field(default=None, description="活载对跨中的弯矩 Mh")
    mz: OptFloat = Field(default=None, description="梁体质量对跨中弯矩 Mz")

    # ---- 应力损失 / 冲击系数 / 剪力滞系数
    sigma15: OptFloat = Field(default=None, description="钢筋松弛应力损失 σ15（MPa）")
    sigma16: OptFloat = Field(default=None, description="混凝土收缩徐变应力损失 σ16（MPa）")
    mul: OptFloat = Field(default=None, description="剪力冲击系数 1+μ")
    mul1: OptFloat = Field(default=None, description="弯矩冲击系数 1+μ1")
    kq: OptFloat = Field(default=None, description="均布荷载剪力滞系数 Kq")
    kp: OptFloat = Field(default=None, description="集中荷载剪力滞系数 Kp")

    # ---- 加载布置
    jack_row: OptInt = Field(default=None, alias="jackRow", description="加载千斤顶行数")
    jack_column: OptInt = Field(default=None, alias="jackColumn", description="加载千斤顶列数")


class StaticLoadDesignDetail(StaticLoadDesignItem):
    """静载参数「通过 id 查询」的 `data` 结构。

    字段与列表行完全一致（文档两份表逐项相同），故直接继承列表行模型，
    避免两份定义漂移；后续若详情接口补充字段，可在此单独覆盖而不用改列表模型。
    """


class StaticLoadPageResponse(BaseCsrdApiResponse[CsrdPageResult[StaticLoadDesignItem]]):
    """静载参数-分页列表查询的完整响应。

    GET /base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignVoPage.ajax
    请求参数（Query）：btdId / bddId / rd / ed / fl 以及其余可选参数（文档把 btdId~fl 标为必须，
    实际上按 bddId 过滤才是常见用法）。
    """


class StaticLoadListResponse(BaseCsrdApiResponse[List[StaticLoadDesignItem]]):
    """静载参数-列表查询的完整响应（`data` 直接是数组）。

    GET /base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignVoList.ajax
    按 bddId 查一条配置时用这个接口，`data[0]` 即该通图号的静载参数。
    """


class StaticLoadDetailResponse(BaseCsrdApiResponse[StaticLoadDesignDetail]):
    """静载参数-通过 id 查询的完整响应（`data` 是单个对象）。

    GET /base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignById.ajax
    请求参数（Query）：btdId（必填）。
    """

#
# __all__ = [
#     # 通用
#     "BaseCsrdApiResponse",
#     "CsrdPageResult",
#     # 通图号
#     "NumberType",
#     "DesignDrawingsNumberItem",
#     "DesignDrawingsNumberDetail",
#     "BddPageResponse",
#     "BddListResponse",
#     "BddDetailResponse",
#     # 静载参数
#     "PsType",
#     "LoadType",
#     "StaticLoadDesignItem",
#     "StaticLoadDesignDetail",
#     "StaticLoadPageResponse",
#     "StaticLoadListResponse",
#     "StaticLoadDetailResponse",
# ]


# ======================================================================================
# 自检：直接运行本文件会喂两份「仿真实返回」样例，验证解析与序列化
#   python bdd_sld_response_models.py
# ======================================================================================
# if __name__ == "__main__":
#     # 样例 1：通图号分页查询。故意包含文档未列的字段（createTime）、数字型枚举（numberType=2）、
#     # 以及空的 prePage（首页），用来验证宽松解析。
#     bdd_page_payload = {
#         "status": "1",
#         "code": 200,  # 数字型 code，应被转成 "200"
#         "message": "操作成功",
#         "timestamp": 1730000000000,
#         "data": {
#             "total": 153,
#             "list": [
#                 {
#                     "bddId": "bdd-0001",
#                     "designDrawingsNumber": "测试通图号-32m双线箱梁-860",
#                     "designBeamType": "860",
#                     "bddSort": "1",  # 文档标 string，这里按 int 解析
#                     "numberType": 2,  # 数字型枚举，应被转成 "2"
#                     "createTime": "2026-11-02 18:00:00",  # 文档未列，extra=allow 保留
#                 },
#                 {
#                     "bddId": "bdd-0002",
#                     "designDrawingsNumber": "国铁内置-100",
#                     "designBeamType": "100",
#                     "bddSort": None,
#                     "numberType": "1",
#                 },
#             ],
#             "pageNum": 1,
#             "pageSize": 10,
#             "size": 2,
#             "startRow": 1,
#             "endRow": 2,
#             "pages": 16,
#             "prePage": "",  # 首页：空串 → None
#             "nextPage": 2,
#             "isFirstPage": True,
#             "isLastPage": False,
#             "hasPreviousPage": False,
#             "hasNextPage": True,
#             "navigatePages": 8,
#             "navigatepageNums": [1, 2, 3, 4, 5, 6, 7, 8],
#             "navigateFirstPage": 1,
#             "navigateLastPage": 8,
#         },
#     }
#     page = BddPageResponse.model_validate(bdd_page_payload)
#     assert page.code == "200", page.code
#     assert page.data is not None and page.data.total == 153
#     assert page.data.pre_page is None, page.data.pre_page
#     first = page.data.list[0]
#     assert first.bdd_sort == 1 and first.number_type is NumberType.OTHER
#     assert first.model_extra is not None and "createTime" in first.model_extra
#     print("[OK] 通图号分页响应解析：total=%s，首条=%s / numberType=%s"
#           % (page.data.total, first.design_drawings_number, first.number_type.value))
#
#     # 样例 2：静载参数按 bddId 查列表。数值用字符串、可选参数缺省、fl 为比值文本。
#     sld_list_payload = {
#         "status": "1",
#         "code": "200",
#         "message": "操作成功",
#         "timestamp": 1730000000000,
#         "data": [
#             {
#                 "btdId": "btd-9527",
#                 "bddId": "bdd-0001",
#                 "rd": "50",  # 字符串数值 → 50.0
#                 "ed": 34.5,
#                 "fl": "1/800",
#                 "psType": "1",
#                 "loadType": 0,  # 数字型枚举 → "0"
#                 "jackRow": "2",
#                 "jackColumn": 3,
#                 "kf": None,
#                 "w0": "",
#             }
#         ],
#     }
#     lst = StaticLoadListResponse.model_validate(sld_list_payload)
#     assert lst.data is not None and len(lst.data) == 1
#     cfg = lst.data[0]
#     assert cfg.rd == 50.0 and cfg.ed == 34.5
#     assert cfg.ps_type is PsType.FULL_PRESTRESS and cfg.load_type is LoadType.ZHONG_HUOZAI
#     assert cfg.jack_row == 2 and cfg.jack_column == 3
#     assert cfg.w0 is None and cfg.mz is None
#     print("[OK] 静载参数列表响应解析：btdId=%s，rd=%s，fl=%s，psType=%s，loadType=%s"
#           % (cfg.btd_id, cfg.rd, cfg.fl, cfg.ps_type.value, cfg.load_type.value))
#
#     # 样例 3：按 id 查询（单对象）+ 空 data（记录被删 / 未初始化）
#     detail = StaticLoadDetailResponse.model_validate(
#         {"code": "200", "data": {"btdId": "btd-9527", "bddId": "bdd-0001", "rd": 50, "ed": 34.5, "fl": "1/800"}}
#     )
#     assert detail.data is not None and detail.data.btd_id == "btd-9527"
#     empty = BddDetailResponse.model_validate({"code": "200", "message": "操作成功", "data": None})
#     assert empty.data is None
#     print("[OK] 详情/空 data 解析：detail.btdId=%s，空 data=%r" % (detail.data.btd_id, empty.data))
#
#     # 样例 4：空列表 / 用字段名（snake_case）解析——`populate_by_name=True` 保证两种写法都可用
#     empty_list = BddListResponse.model_validate({"code": 200, "data": []})
#     assert empty_list.data == []
#     by_name = DesignDrawingsNumberItem.model_validate(
#         {"bdd_id": "bdd-0003", "design_drawings_number": "按字段名解析", "design_beam_type": "861"}
#     )
#     assert by_name.bdd_id == "bdd-0003" and by_name.design_beam_type == "861"
#     print("[OK] 空列表解析：%r；snake_case 解析：%s" % (empty_list.data, by_name.design_beam_type))
#
#     # 序列化还原成接口原始 JSON：by_alias=True 输出驼峰键，mode="json" 把枚举/日期转成可 JSON 化的值
#     print("[OK] 序列化示例（by_alias=True, mode=json）：%s"
#           % page.data.list[1].model_dump(by_alias=True, mode="json", exclude_none=True))
#     print("全部自检通过。")
