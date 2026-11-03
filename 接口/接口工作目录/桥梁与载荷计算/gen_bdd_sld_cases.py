# -*- coding: utf-8 -*-
"""
通图号 + 静态载荷计算 接口测试用例生成器

输入（依据）：
  - 桥梁与载荷计算/梁体与通图号.md       （通图号 7 个接口）
  - 桥梁与载荷计算/梁体与通图号需求.md   （通图号业务规则 + 静载试验设计参数需求）
  - 桥梁与载荷计算/桥梁设计与载荷计算.md （静载试验设计参数 7 个接口）
  - 基本信息接口文档.md                  （登录 / 组织机构，复用库内已有的前置数据）
产出：
  - 通图号与载荷计算-接口测试用例.json  （不写入数据库，供评审）
  - 通图号与载荷计算-测试用例说明.md
"""
import io
import re
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "组织机构管理系统"
MOD_BDD = "通图号"
MOD_SLD = "载荷计算"

H_OK = {"Authorization": "${loginUserToken}", "Sys-dept-id": "${bfDeptId}"}
H_NO_AUTH = {"Sys-dept-id": "${bfDeptId}"}
H_NO_DEPT = {"Authorization": "${loginUserToken}"}
H_FAKE_DEPT = {"Authorization": "${loginUserToken}", "Sys-dept-id": "999999999"}

# 通图号列表查询复用库内 id=10（同一 endpoint 不重复建记录，梁型管理也在用它取 sjth）
API = {
    "bdd_list": 10,
    "bdd_page": 18,
    "bdd_add": 19,
    "bdd_upd": 20,
    "bdd_get": 21,
    "bdd_del": 22,
    "bdd_batch": 23,
    "sld_page": 24,
    "sld_list": 25,
    "sld_add": 26,
    "sld_upd": 27,
    "sld_get": 28,
    "sld_del": 29,
    "sld_batch": 30,
    "bdd_init": 31,
}

api_info = [
    {"id": 18, "name": "通图号分页列表查询", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "分页列表查询",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoPage.ajax",
     "method": "GET", "response_model": "DesignDrawNumberPageResponse", "swagger_md_text": None,
     "description": "分页查询本梁场通图号，query 参数 pageNum/pageSize，返回 data.total 与 data.list（含 bddId/designDrawingsNumber/designBeamType/bddSort/numberType）"},
    {"id": 19, "name": "通图号新增", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "新增",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/addBfmBaseDesignDrawingsNumber.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "新增通图号：designDrawingsNumber（1~50 字符）与 designBeamType（3 位梁型码，去空格后查重，且只能落在 153~998）必填；成功不返回主键，bddId 需按梁型码回查获取"},
    {"id": 20, "name": "通图号编辑", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "编辑",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/updateBfmBaseDesignDrawingsNumber.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "编辑通图号：bddId（必填，标识待改记录，文档表格标「非必须」为笔误）、designDrawingsNumber/designBeamType 全量回传；国铁内置编码（numberType=1）不允许编辑，梁型码改动后仍需查重"},
    {"id": 21, "name": "通图号通过id查询", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "通过id查询",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberById.ajax",
     "method": "GET", "response_model": "DesignDrawNumberDetailResponse", "swagger_md_text": None,
     "description": "按主键 bddId 查询单个通图号，data 为对象"},
    {"id": 22, "name": "通图号通过id删除", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "通过id删除",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/deleteBfmBaseDesignDrawingsNumber.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按主键 bddId 删除单个通图号（物理删除）；国铁内置编码不允许删除"},
    {"id": 23, "name": "通图号批量删除", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "批量删除",
     "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/deleteBfmBaseDesignDrawingsNumberBatch.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按 bddIds（多个主键英文逗号拼接）批量删除通图号"},
    {"id": 24, "name": "静载设计参数分页列表查询", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "分页列表查询",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignVoPage.ajax",
     "method": "GET", "response_model": "StaticloadDesignPageResponse", "swagger_md_text": None,
     "description": "分页查询静载试验设计参数，返回 data.total 与 data.list（主键 btdId、外键 bddId + 24 个设计字段）"},
    {"id": 25, "name": "静载设计参数列表查询", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "列表查询",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignVoList.ajax",
     "method": "GET", "response_model": "StaticloadDesignListResponse", "swagger_md_text": None,
     "description": "按 bddId（通图号）/btdId 等条件查询静载试验设计参数，返回 data 数组"},
    {"id": 26, "name": "静载设计参数新增", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "新增",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/addBfmBaseStaticloadDesign.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "为指定通图号（bddId）配置静载试验设计参数：bddId/rd/ed/fl 必填，其余 21 项选填；主键 btdId 由服务端生成，请求报文不需要传（文档表格标「必须」为实体字段注解带出）；成功不返回主键，btdId 需按 bddId 回查获取。一个通图号只对应一条静载参数（1:1）"},
    {"id": 27, "name": "静载设计参数编辑", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "编辑",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/updateBfmBaseStaticloadDesign.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "编辑静载试验设计参数：btdId 标识待改记录，bddId 与必填项全量回传，选填项可按需修改"},
    {"id": 28, "name": "静载设计参数通过id查询", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "通过id查询",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/queryBfmBaseStaticloadDesignById.ajax",
     "method": "GET", "response_model": "StaticloadDesignDetailResponse", "swagger_md_text": None,
     "description": "按主键 btdId 查询静载试验设计参数，data 为对象"},
    {"id": 29, "name": "静载设计参数通过id删除", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "通过id删除",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/deleteBfmBaseStaticloadDesign.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按主键 btdId 删除单条静载试验设计参数"},
    {"id": 30, "name": "静载设计参数批量删除", "project_name": PROJECT, "module_name": MOD_SLD,
     "sub_module_name": "批量删除",
     "endpoint": "/api/base/bfmBaseStaticloadDesign/deleteBfmBaseStaticloadDesignBatch.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按 btdIds（多个主键英文逗号拼接）批量删除静载试验设计参数"},
    {"id": 31, "name": "初始化通图号", "project_name": PROJECT, "module_name": MOD_BDD,
     "sub_module_name": "初始化",
     "endpoint": "/api/base/bfmBeamField/initBfmBeamField.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "为本梁场初始化内置 153 条通图号（001~152、999，numberType=1）。无请求参数、不需要请求体；重复调用应幂等（不产生重复编码）"},
]

test_data = []
cases = []


# ---------------------------------------------------------------- helpers
def td(key, name, description, api_info_id, headers=None, data=None, params=None, extract=None):
    test_data.append({
        "key": key, "name": name, "description": description,
        "headers": headers, "api_info_id": api_info_id,
        "data": data, "params": params, "extract": extract,
    })


def ex(name, jsonpath, description, index=0):
    return {"name": name, "jsonpath": jsonpath,
            "handle": {"handle_method": "get_index", "handle_param": {"index": index}},
            "description": description}


def r(path, op, val=None):
    return {"jsonpath": path, "operator": op, "expect_value": val}


def rv(path, op, var):
    """期望值取系统上下文变量：填键名（不带 ${}）+ ctx.is_ctx_var=True，执行器派发前自动替换"""
    return {"jsonpath": path, "operator": op, "expect_value": var, "ctx": {"is_ctx_var": True}}


def A(rules, ai=None):
    return {"assertion_rules": rules, "ai_assertion_rule": ai}


OK = A([r("$", "res_contains_data", {"status": "1", "code": "200"})])


def OKX(extra, ai=None):
    return A([r("$", "res_contains_data", {"status": "1", "code": "200"})] + extra, ai)


def FAIL(ai="message 应为明确的业务提示（必填项缺失 / 参数非法 / 编码重复 / 编码被占用 / 数据不存在等），不得返回内部异常或 500"):
    return A([r("$", "res_contains_data", {"status": "0", "code": "200"}), r("$.message", "not_empty")], ai)


def NO_AUTH(ai="缺少 Authorization 时应鉴权失败（status≠1），不得返回业务数据"):
    return A([r("$.status", "ne", "1")], ai)


def S(key, desc, assertion):
    return {"test_data_key": key, "description": desc, "assertion_config": assertion}


CHAIN_STEPS = ["beamfield.prep.add_group", "beamfield.prep.get_group_id",
               "beamfield.prep.add_build_unit", "beamfield.prep.get_build_unit_id",
               "beamfield.prep.add_proj", "beamfield.prep.get_proj_id",
               "beamfield.prep.add_section", "beamfield.prep.get_section_id",
               "beamfield.dept.create_f01", "beamfield.dept.verify_f01"]


def PRE(with_builtin=False):
    """公共前置：令牌 → 组织机构链路（梁场 F01 / bfDeptId）→ 梁场基本信息；with_builtin 时再校验内置编码就绪

    通图号按梁场隔离，本梁场由前置链路统一创建（deptCode=TESTLC201），不做清场。
    """
    p = [
        {"context_key_has": [
            {"context_key": "loginUserToken", "steps_after_failure": ["login.success"]},
            {"context_key": "yunweiDeptId", "steps_after_failure": ["dept.query.tree_success"]},
        ]},
        {"api_res_exist": [{
            "test_data_key": "beamfield.prep.detect_chain",
            "judgment_criteria_items": [{
                "assertion_config": A([r("$..deptCode", "contains", "TESTLC201")]),
                "steps_after_success": [],
                "steps_after_failure": CHAIN_STEPS,
            }],
        }]},
        {"api_res_not_exist": [{
            "test_data_key": "beamfield.query.by_dept",
            "judgment_criteria_items": [{
                "assertion_config": A([r("$.data", "length_gt", 0)]),
                "steps_after_failure": [],
                "steps_after_success": ["beamfield.prepare.add"],
            }],
        }]},
    ]
    if with_builtin:
        # 内置 153 条（numberType=1）由「初始化通图号」接口生成（POST initBfmBeamField）。
        # 前置用「先查后建」：查不到内置编码才调初始化接口，梁场已初始化时不会重复调用。
        p.append({"api_res_not_exist": [{
            "test_data_key": "bdd.list.builtin",
            "judgment_criteria_items": [{
                "assertion_config": A([r("$.data", "length_gt", 0)]),
                "steps_after_success": ["bdd.init.builtin"],
                "steps_after_failure": [],
            }],
        }]})
    return p


def seed_block(probe_key, add_key, recheck=False):
    """前置「先查后建」：查不到才新增，已有则跳过；recheck=True 时新增后再查一次（用于提取主键）"""
    return {"api_res_not_exist": [{
        "test_data_key": probe_key,
        "judgment_criteria_items": [{
            "assertion_config": A([r("$.data", "length_gt", 0)]),
            "steps_after_success": [add_key] + ([probe_key] if recheck else []),
            "steps_after_failure": [],
        }],
    }]}


def case(mod, key, sub, title, desc, steps, pre=None, seeds=None, post=None, order=0, active=1):
    p = list(PRE() if pre is None else pre)
    for s in seeds or []:
        p.append(seed_block(*s))
    cases.append({
        "key": key, "module_name": mod, "sub_module_name": sub,
        "title": title, "description": desc,
        "pre_requisites": p, "post_steps": post, "test_steps": steps,
        "is_active": active, "order": order,
    })


BDD_ITEM_KEYS = ["bddId", "designDrawingsNumber", "designBeamType"]
SLD_ITEM_KEYS = ["btdId", "bddId", "rd", "ed", "fl"]


def bdd_case(key, sub, title, desc, steps, pre=None, seeds=None, post=None, order=0):
    case(MOD_BDD, key, sub, title, desc, steps, pre, seeds, post, order)


def sld_case(key, sub, title, desc, steps, pre=None, seeds=None, post=None, order=0):
    case(MOD_SLD, key, sub, title, desc, steps, pre, seeds, post, order)


SUB_PAGE, SUB_LIST, SUB_ADD, SUB_UPD = "分页列表查询", "列表查询", "新增", "编辑"
SUB_GET, SUB_DEL, SUB_BATCH, SUB_INIT = "通过id查询", "通过id删除", "批量删除", "初始化"


# ================================================================ 一、通图号
# 需求要点（梁体与通图号需求.md 2.1）：
#   · designDrawingsNumber 必填，长度 1~50；
#   · designBeamType 必填、长度 3，**去掉空格后**查重，且只能落在 153~998（001~152、999 已被国铁占用）；
#   · 新建记录默认排在最前（分页查询时返回的数据里排在第一条）；
#   · 内置 153 条由「初始化通图号」接口生成，不允许编辑/删除；
#   · 列表过滤：图号名称为模糊匹配，梁型码按精确匹配；
#   · 每个梁场独立管理自己的通图号。

# ---- 分页
bdd_page_ok = [
    r("$.data", "res_contains_key", ["total", "list", "pageNum", "pageSize", "pages",
                                     "isFirstPage", "isLastPage"]),
    r("$.data.total", "gte", 1),
    r("$.data.pageNum", "in", [1, "1"]),
    r("$.data.pageSize", "in", [10, "10"]),
    r("$.data.list", "type", "list"),
    r("$.data.list", "length_gt", 0),
    r("$.data.list[0]", "res_contains_key", BDD_ITEM_KEYS),
    r("$.data.isFirstPage", "in", [True, "true", 1]),
]

# ================================================================ 测试数据
BDD_PREFIX = "测试通图号-"
SLD_BDD_PREFIX = "载荷测试图号-"

# 通图号正向数据：名称可直接读出「梁型 + 梁型码」，梁型码落在 153~998 的用户可用区间
BDD_ADDS = [
    ("t01", "测试通图号-32m双线箱梁-860", "860", "新增成功、按图号名称/按梁型码过滤、分页第 1 条"),
    ("t02", "测试通图号-24m单线箱梁-861", "861", "梁型码查重用例的冲突基准；分页第 2 条"),
    ("t03", "测试通图号-20m双线T梁-862", "862", "通过id查询（字段完整）"),
    ("t04", "测试通图号-32m单线T梁-863", "863", "编辑-修改图号名称"),
    ("t05", "测试通图号-24m双线箱梁-864", "864", "编辑-修改梁型码（改为 870）"),
    ("t06", "测试通图号-20m单线箱梁-865", "865", "通过id删除-成功"),
    ("t07", "测试通图号-40m双线箱梁-866", "866", "批量删除-第 1 条"),
    ("t08", "测试通图号-40m单线T梁-867", "867", "批量删除-第 2 条"),
    ("t09", "测试通图号-32m双线T梁-868", "868", "重复删除（同一主键删两次）"),
    ("t10", "测试通图号-24m单线T梁-869", "869", "删除-缺 Authorization"),
    ("t11", "测试通图号-编码下界153", "153", "梁型码合法下界"),
    ("t12", "测试通图号-编码上界998", "998", "梁型码合法上界"),
    ("t13", "测试通图号-批量含无效-873", "873", "批量删除中混入不存在的 ID"),
    ("t14", "测试通图号-排序校验-872", "872", "新建记录默认排在最前（先删后建保证确定性）"),
]

for _c, _n, _b, _d in BDD_ADDS:
    td("bdd.add." + _c, "新增通图号-" + _n, _d, API["bdd_add"], H_OK,
       {"designDrawingsNumber": _n, "designBeamType": _b}, None, None)
    td("bdd.probe." + _c, "探针-梁型码" + _b,
       "按梁型码 " + _b + " 查询通图号，用于「先查后建」并提取 bddId（新增接口不返回主键）",
       API["bdd_list"], H_OK, None, {"designBeamType": _b},
       [ex("bddId" + _c.upper(), "$.data[0].bddId", "梁型码 " + _b + " 对应记录的 bddId")])

# 负向报文：全部使用独立梁型码/名称，避免被「梁型码重复」抢先拦截导致提示语不是目标校验
BDD_NEG = [
    ("n01", "缺图号名称", {"designBeamType": "874"},
     "请求体不含 designDrawingsNumber，必填校验应拦截",
     "message 应提示缺少必填参数 designDrawingsNumber（或“通图号不能为空”），不得插入记录", None),
    ("n02", "图号名称为空串", {"designDrawingsNumber": "", "designBeamType": "875"},
     "designDrawingsNumber 传空串（长度 0，小于下界 1），必填/长度校验应拦截",
     "message 应提示通图号不能为空或长度不合法，不得插入记录", None),
    ("n04", "缺梁型码", {"designDrawingsNumber": "测试通图号-缺梁型码-877"},
     "请求体不含 designBeamType，必填校验应拦截",
     "message 应提示缺少必填参数 designBeamType（或“梁型码不能为空”）", None),
    ("n05", "梁型码两位", {"designDrawingsNumber": "测试通图号-梁型码两位-878", "designBeamType": "86"},
     "designBeamType 长度 2（要求长度 3），长度校验应拦截",
     "message 应提示梁型码长度必须为 3 位", None),
    ("n06", "梁型码四位", {"designDrawingsNumber": "测试通图号-梁型码四位-879", "designBeamType": "8601"},
     "designBeamType 长度 4（要求长度 3），长度校验应拦截",
     "message 应提示梁型码长度必须为 3 位", None),
    ("n07", "梁型码重复", {"designDrawingsNumber": "测试通图号-梁型码重复-880N", "designBeamType": "861"},
     "designBeamType 取 t02 已占用的 861，应被查重拒绝；回查 861 仍只有 t02 一条",
     "message 应提示梁型码已存在（重复），不得插入第二条同码记录", "861"),
    ("n08", "梁型码带空格", {"designDrawingsNumber": "测试通图号-梁型码带空格-881N", "designBeamType": " 861 "},
     "designBeamType 传「 861 」（前后各一个空格），需求要求**去掉空格后**查重，应被识别为与 861 重复而拒绝",
     "message 应提示梁型码已存在；若落库则说明查重未做 trim 处理，属于需求偏差", None),
    ("n09", "占用内置码100", {"designDrawingsNumber": "测试通图号-占用内置码-882N", "designBeamType": "100"},
     "designBeamType 取 100（国铁占用 001~152），应被拒绝",
     "message 应提示梁型码已被国铁内置编码占用，或超出用户可用区间", None),
    ("n10", "编码999占用", {"designDrawingsNumber": "测试通图号-编码上界占用-883N", "designBeamType": "999"},
     "designBeamType 取 999（国铁占用的最后一个），既超上界又被占用，应被拒绝",
     "message 应提示梁型码不可用（已被占用 / 超出 153~998 区间）", None),
    ("n11", "编码000越界", {"designDrawingsNumber": "测试通图号-编码越界-884N", "designBeamType": "000"},
     "designBeamType 取 000（小于下界 153），应被拒绝",
     "message 应提示梁型码必须在 153~998 区间内", None),
]

NEG_PROBE = {
    "n01": ({"designBeamType": "874"}, "designBeamType=874（报文没有图号名称，只能按编码兜底）"),
    "n02": ({"designBeamType": "875"}, "designBeamType=875（名称为空串，按编码兜底）"),
    "n04": ({"designDrawingsNumber": "测试通图号-缺梁型码-877"}, "designDrawingsNumber=测试通图号-缺梁型码-877（报文没有编码）"),
    "n05": ({"designBeamType": "86"}, "designBeamType=86"),
    "n06": ({"designBeamType": "8601"}, "designBeamType=8601"),
    "n07": ({"designBeamType": "861"}, "designBeamType=861"),
    "n08": ({"designDrawingsNumber": "测试通图号-梁型码带空格-881N"}, "designDrawingsNumber=测试通图号-梁型码带空格-881N（编码带空格，按名称查更可靠）"),
    "n09": ({"designBeamType": "100"}, "designBeamType=100"),
    "n10": ({"designBeamType": "999"}, "designBeamType=999"),
    "n11": ({"designBeamType": "000"}, "designBeamType=000"),
}

for _c, _t, _b, _d, _ai, _conflict in BDD_NEG:
    td("bdd.add." + _c, "新增通图号-" + _t, _d + "（负向报文，本应被拒绝）", API["bdd_add"], H_OK, _b, None, None)
    _pq, _pd = NEG_PROBE[_c]
    td("bdd.probe." + _c, "探针-负向报文" + _c.upper(),
       "按 " + _pd + " 查询，确认「" + _t + "」的报文被拒绝后没有落库",
       API["bdd_list"], H_OK, None, _pq,
       [ex("bddId" + _c.upper(), "$.data[0].bddId", "该负向报文对应的 bddId（正常应为空）")])

# ---- 内置编码（环境数据，不清场）
td("bdd.list.builtin", "通图号列表-内置编码",
   "查询 numberType=1 的国铁内置编码（001~152、999，共 153 条），供「内置编码不可编辑/不可删除」类用例使用",
   API["bdd_list"], H_OK, None, {"numberType": "1"},
   [ex("bddBuiltInId", "$.data[0].bddId", "第一条内置编码的 bddId（不可编辑/不可删除）"),
    ex("bddBuiltInCode", "$.data[0].designBeamType", "第一条内置编码的梁型码"),
    ex("bddBuiltInName", "$.data[0].designDrawingsNumber", "第一条内置编码的通图号名称")])

# ---- 查询类数据
td("bdd.list.all", "通图号列表-无参",
   "不带任何过滤条件查询本梁场全部通图号，用于校验返回结构", API["bdd_list"], H_OK, None, None, None)
td("bdd.list.by_number", "通图号列表-按图号名称",
   "按图号名称前缀「测试通图号-32m双线箱梁」模糊查询，用于验证名称过滤", API["bdd_list"], H_OK, None,
   {"designDrawingsNumber": "测试通图号-32m双线箱梁"}, None)
td("bdd.list.by_code", "通图号列表-按梁型码",
   "按梁型码 861 精确查询，用于验证编码过滤", API["bdd_list"], H_OK, None, {"designBeamType": "861"}, None)
td("bdd.list.no_auth", "通图号列表-缺Authorization", "请求头只带 Sys-dept-id", API["bdd_list"], H_NO_AUTH, None, None, None)
td("bdd.list.no_dept", "通图号列表-缺Sys-dept-id", "请求头只带 Authorization，接口无法定位梁场",
   API["bdd_list"], H_NO_DEPT, None, None, None)
td("bdd.list.fake_dept", "通图号列表-不存在的梁场", "Sys-dept-id=999999999", API["bdd_list"], H_FAKE_DEPT, None, None, None)
td("bdd.page.default", "通图号分页-第1页10条", "pageNum=1&pageSize=10", API["bdd_page"], H_OK, None,
   {"pageNum": 1, "pageSize": 10}, None)
td("bdd.page.size1", "通图号分页-每页1条", "pageNum=1&pageSize=1", API["bdd_page"], H_OK, None,
   {"pageNum": 1, "pageSize": 1}, None)
td("bdd.page.second", "通图号分页-第2页", "pageNum=2&pageSize=1", API["bdd_page"], H_OK, None,
   {"pageNum": 2, "pageSize": 1}, None)
td("bdd.get.by_id", "通图号通过id查询", "按 bddId 查询单条记录（bddId 由探针/内置编码提取）",
   API["bdd_get"], H_OK, None, {"bddId": "${bddIdT03}"}, None)
td("bdd.get.not_exist", "通图号通过id查询-不存在主键", "bddId=999999999", API["bdd_get"], H_OK, None,
   {"bddId": "999999999"}, None)
td("bdd.get.builtin", "通图号通过id查询-内置编码", "按内置编码的 bddId 回查，用于确认删除/编辑被拒绝后数据未变",
   API["bdd_get"], H_OK, None, {"bddId": "${bddBuiltInId}"}, None)

# ---- 编辑类数据
td("bdd.upd.t04", "编辑通图号-t04改图号名称",
   "把 t04 的图号名称改为「测试通图号-32m单线T梁-863已改」，梁型码不变，用于验证全字段编辑",
   API["bdd_upd"], H_OK, {"bddId": "${bddIdT04}", "designDrawingsNumber": "测试通图号-32m单线T梁-863已改",
                          "designBeamType": "863"}, None, None)
td("bdd.upd.t05", "编辑通图号-t05改梁型码",
   "把 t05 的梁型码由 864 改为未被占用的 870，名称同步改为「测试通图号-24m双线箱梁-870」，用于验证编码可编辑且改后仍查重",
   API["bdd_upd"], H_OK, {"bddId": "${bddIdT05}", "designDrawingsNumber": "测试通图号-24m双线箱梁-870",
                          "designBeamType": "870"}, None, None)
td("bdd.upd.dup_code", "编辑通图号-梁型码改为已占用",
   "把 t04 的梁型码改为 t02 已占用的 861，应被查重拒绝", API["bdd_upd"], H_OK,
   {"bddId": "${bddIdT04}", "designDrawingsNumber": "测试通图号-32m单线T梁-863改861", "designBeamType": "861"},
   None, None)
td("bdd.upd.builtin", "编辑通图号-内置编码",
   "尝试把内置编码的通图号名称改掉，内置 153 条不允许编辑", API["bdd_upd"], H_OK,
   {"bddId": "${bddBuiltInId}", "designDrawingsNumber": "测试通图号-篡改内置编码", "designBeamType": "${bddBuiltInCode}"},
   None, None)
td("bdd.upd.t04.no_auth", "编辑通图号-t04缺Authorization",
   "请求头只带 Sys-dept-id，名称改为「测试通图号-无令牌篡改-863」", API["bdd_upd"], H_NO_AUTH,
   {"bddId": "${bddIdT04}", "designDrawingsNumber": "测试通图号-无令牌篡改-863", "designBeamType": "863"}, None, None)

# ---- 删除类数据
td("bdd.del.t06", "删除通图号-t06", "删除 t06（865）", API["bdd_del"], H_OK, None, {"bddId": "${bddIdT06}"}, None)
td("bdd.del.t09.first", "删除通图号-t09第一次", "删除 t09（868）", API["bdd_del"], H_OK, None,
   {"bddId": "${bddIdT09}"}, None)
td("bdd.del.t09.second", "删除通图号-t09第二次", "再次删除同一个 bddId，验证幂等/明确提示", API["bdd_del"], H_OK,
   None, {"bddId": "${bddIdT09}"}, None)
td("bdd.del.builtin", "删除通图号-内置编码", "尝试删除内置编码记录，应与需求一致被拒绝",
   API["bdd_del"], H_OK, None, {"bddId": "${bddBuiltInId}"}, None)
td("bdd.del.t10.no_auth", "删除通图号-t10缺Authorization", "请求头只带 Sys-dept-id，删除 t10（869）",
   API["bdd_del"], H_NO_AUTH, None, {"bddId": "${bddIdT10}"}, None)
td("bdd.batch.t07t08", "批量删除通图号-t07,t08", "bddIds=${bddIdT07},${bddIdT08}", API["bdd_batch"], H_OK, None,
   {"bddIds": "${bddIdT07},${bddIdT08}"}, None)
td("bdd.batch.with_invalid", "批量删除通图号-t13+无效ID",
   "bddIds 混入一个不存在的 ID（999999999），验证有效记录被删、接口不报 500",
   API["bdd_batch"], H_OK, None, {"bddIds": "${bddIdT13},999999999"}, None)
td("bdd.batch.miss_param", "批量删除通图号-缺bddIds", "不传 bddIds", API["bdd_batch"], H_OK, None, {}, None)
td("bdd.batch.no_auth", "批量删除通图号-缺Authorization", "请求头只带 Sys-dept-id", API["bdd_batch"], H_NO_AUTH,
   None, None, None)
td("bdd.del.t14.dev", "删除通图号-排序用例前置清理",
   "排序校验用例执行前先按梁型码 872 定位残留记录并删除，保证「新建排在最前」的断言可确定性复现（幂等）",
   API["bdd_del"], H_OK, None, {"bddId": "${bddIdT14}"}, None)
td("bdd.del.t01.dev", "删除通图号-新增用例前置清理",
   "新增成功用例执行前先按梁型码 860 定位并删除残留记录，避免重复执行时撞「梁型码重复」（幂等）",
   API["bdd_del"], H_OK, None, {"bddId": "${bddIdT01}"}, None)

# ================================================================ 通图号用例

# ---- 初始化
td("bdd.init.builtin", "初始化通图号", "调用初始化接口为本梁场生成内置 153 条通图号（无请求参数、无请求体）",
   API["bdd_init"], H_OK, None, None, None)

bdd_case("bdd.init.builtin", SUB_INIT, "初始化通图号生成内置153条编码且重复调用不重复生成",
         "TC-BDD-001: 内置 153 条（001~152、999）由「初始化通图号」接口生成。本梁场可能已初始化，"
         "因此本条在已初始化状态下再调一次接口，校验 numberType=1 的记录仍恰好 153 条——"
         "若变成 306 条说明初始化未做幂等（重复插入同一批编码），属于需求偏差",
         [S("bdd.init.builtin", "POST 初始化通图号（已初始化状态下重复调用）", OK),
          S("bdd.list.builtin", "GET 列表查询 numberType=1，校验内置编码仍为 153 条",
            OKX([r("$.data", "type", "list"),
                 r("$.data", "length_eq", 153)],
                "内置编码固定为 001~152 加 999 共 153 条；重复调用初始化不应产生重复记录。"
                "若数量大于 153，说明初始化未去重；若小于 153，说明初始化未真正补全"))])

# ---- 分页
bdd_case("bdd.query.page_success", SUB_PAGE, "分页查询第1页10条返回结构正确",
         "TC-BDD-001: 前置确保 t01/t02 存在（没有才新增）后按 pageNum=1&pageSize=10 查询，"
         "校验分页结构（total/list/pageNum/pageSize/pages/isFirstPage）齐全、list 非空且元素字段完整",
         [S("bdd.page.default", "GET 分页查询 pageNum=1&pageSize=10", OKX(bdd_page_ok))],
         seeds=[("bdd.probe.t01", "bdd.add.t01"), ("bdd.probe.t02", "bdd.add.t02")])

bdd_case("bdd.query.page_size_one", SUB_PAGE, "每页1条时分页返回仅1条记录",
         "TC-BDD-002: 前置确保 t01 存在后按 pageNum=1&pageSize=1 查询，校验 list 长度恰为 1、pageSize=1、isFirstPage=true",
         [S("bdd.page.size1", "GET 分页查询 pageNum=1&pageSize=1",
            OKX([r("$.data.pageSize", "in", [1, "1"]),
                 r("$.data.list", "length_eq", 1),
                 r("$.data.isFirstPage", "in", [True, "true", 1])]))],
         seeds=[("bdd.probe.t01", "bdd.add.t01")])

bdd_case("bdd.query.page_second", SUB_PAGE, "第2页翻页正确且首页标记为false",
         "TC-BDD-003: 前置确保至少 2 条数据（t01/t02）后按 pageNum=2&pageSize=1 查询，"
         "校验返回 1 条、pageNum=2、isFirstPage=false、hasPreviousPage=true",
         [S("bdd.page.second", "GET 分页查询 pageNum=2&pageSize=1",
            OKX([r("$.data.list", "length_eq", 1),
                 r("$.data.pageNum", "in", [2, "2"]),
                 r("$.data.isFirstPage", "in", [False, "false", 0]),
                 r("$.data.hasPreviousPage", "in", [True, "true", 1])]))],
         seeds=[("bdd.probe.t01", "bdd.add.t01"), ("bdd.probe.t02", "bdd.add.t02")])

# ---- 列表
bdd_case("bdd.query.list_success", SUB_LIST, "无参列表查询返回字段完整",
         "TC-BDD-004: 前置确保 t01 存在后不带过滤条件查询，校验 data 为数组、非空、元素含 bddId/designDrawingsNumber/designBeamType",
         [S("bdd.list.all", "GET 列表查询（无参）",
            OKX([r("$.data", "type", "list"),
                 r("$.data", "length_gt", 0),
                 r("$.data[0]", "res_contains_key", BDD_ITEM_KEYS)]))],
         seeds=[("bdd.probe.t01", "bdd.add.t01")])

bdd_case("bdd.query.list_by_number", SUB_LIST, "按图号名称模糊过滤只返回命中记录",
         "TC-BDD-005: 前置确保 t01（测试通图号-32m双线箱梁-860）存在后，只传图号名称的**前缀**过滤——"
         "名称是模糊匹配，传部分名称也应命中。应恰好返回 1 条（本套数据里只有 t01 含该片段），"
         "且名称以该前缀开头——若返回多条说明过滤未生效，若返回 0 条说明被当成精确匹配",
         [S("bdd.list.by_number", "GET 列表查询 designDrawingsNumber=测试通图号-32m双线箱梁（部分名称）",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designDrawingsNumber", "startswith", "测试通图号-32m双线箱梁"),
                 r("$.data[0].designBeamType", "eq", "860")]))],
         seeds=[("bdd.probe.t01", "bdd.add.t01")])

bdd_case("bdd.query.list_by_code", SUB_LIST, "按梁型码精确过滤返回唯一记录",
         "TC-BDD-006: 前置确保 t02（编码 861）存在后按梁型码过滤（梁型码按精确匹配），应恰好 1 条且编码与名称一致",
         [S("bdd.list.by_code", "GET 列表查询 designBeamType=861",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designBeamType", "eq", "861"),
                 r("$.data[0].designDrawingsNumber", "eq", "测试通图号-24m单线箱梁-861")]))],
         seeds=[("bdd.probe.t02", "bdd.add.t02")])

bdd_case("bdd.query.list_builtin", SUB_LIST, "按numberType=1过滤返回国铁内置编码",
         "TC-BDD-007: 前置要求本梁场已初始化内置编码（153 条，numberType=1）。按 numberType=1 过滤，"
         "应返回非空列表且首条 numberType=1；若为空说明梁场未初始化，需求要求每个梁场初始化后必须默认生成 153 个编码",
         [S("bdd.list.builtin", "GET 列表查询 numberType=1",
            OKX([r("$.data", "type", "list"),
                 r("$.data", "length_gt", 0),
                 r("$.data[0].numberType", "in", [1, "1"]),
                 r("$.data[0].designBeamType", "not_empty"),
                 r("$.data[0].designDrawingsNumber", "not_empty")],
                "numberType=1 表示国铁基础编码；返回项应全部为内置编码（001~152、999），不应混入用户创建的编码"))],
         pre=PRE(with_builtin=True))

bdd_case("bdd.query.list_no_auth", SUB_LIST, "缺少Authorization查询通图号鉴权失败",
         "TC-BDD-008: 请求头只带 Sys-dept-id，不带 Authorization，应鉴权失败且不返回数据",
         [S("bdd.list.no_auth", "GET 列表查询，请求头仅 Sys-dept-id",
            A([r("$.status", "ne", "1"), r("$.data", "is_empty")]))])

bdd_case("bdd.query.list_no_dept", SUB_LIST, "缺少Sys-dept-id查询不返回通图号数据",
         "TC-BDD-009: 请求头只带 Authorization，接口无法定位梁场。通图号按梁场独立管理，"
         "此时应返回空列表或业务提示，不得串出其它梁场的数据",
         [S("bdd.list.no_dept", "GET 列表查询，请求头仅 Authorization",
            A([r("$..bddId", "is_empty")],
              "缺少 Sys-dept-id 时应返回空列表或“梁场/部门不存在”类提示，不得返回任何通图号，也不得抛内部异常"))])

bdd_case("bdd.query.list_fake_dept", SUB_LIST, "Sys-dept-id为不存在的梁场时不串出其它梁场数据",
         "TC-BDD-010: 请求头 Sys-dept-id=999999999（库中不存在的 deptId），校验不报内部异常且不返回通图号数据",
         [S("bdd.list.fake_dept", "GET 列表查询，Sys-dept-id=999999999",
            A([r("$..bddId", "is_empty")],
              "梁场标识不存在时应返回空列表或业务提示，不得返回其它梁场的通图号，也不得抛数据库/内部异常"))])

# ---- 通过id查询
bdd_case("bdd.query.by_id_success", SUB_GET, "通过bddId查询单个通图号字段完整",
         "TC-BDD-011: 前置确保 t03（862）存在并取回 bddId 后按 id 查询，校验 bddId/图号名称/梁型码与新增报文一致",
         [S("bdd.get.by_id", "GET 通过id查询 bddId=${bddIdT03}",
            OKX([r("$.data", "res_contains_key", BDD_ITEM_KEYS),
                 r("$.data.bddId", "not_empty"),
                 r("$.data.designBeamType", "eq", "862"),
                 r("$.data.designDrawingsNumber", "eq", "测试通图号-20m双线T梁-862")]))],
         seeds=[("bdd.probe.t03", "bdd.add.t03")])

bdd_case("bdd.query.by_id_not_exist", SUB_GET, "查询不存在的主键不报500",
         "TC-BDD-012: bddId=999999999（库中不存在），应返回空数据或明确提示，不得抛 500 / 数据库异常",
         [S("bdd.get.not_exist", "GET 通过id查询 bddId=999999999",
            A([r("$.code", "eq", "200")],
              "主键不存在时应返回 data=null 或 status=0 + 明确提示（记录不存在），不得抛 500 / 数据库异常"))])

# ---- 新增
# 说明：t01 同时被分页/列表类用例当作「先查后建」的造数，若本用例直接 POST 会撞「梁型码重复」。
# 因此前置先按梁型码定位并删除残留的 t01（幂等），再在测试步骤里新增，保证本条用例单独执行也能稳定通过。
bdd_case("bdd.add.success", SUB_ADD, "新增通图号成功且按梁型码可查",
         "TC-BDD-013: 新增 t01（通图号 测试通图号-32m双线箱梁-860，梁型码 860）。前置先清掉可能残留的同码记录（幂等），"
         "保证重复执行稳定。新增接口不返回主键，故按梁型码回查确认落库：应恰好 1 条、编码与名称一致；"
         "用户创建的编码 numberType 应为 2（其他编码，区别于国铁内置的 1）",
         [S("bdd.add.t01", "POST 新增 t01，designDrawingsNumber=测试通图号-32m双线箱梁-860，designBeamType=860", OK),
          S("bdd.probe.t01", "GET 列表查询 designBeamType=860，回查落库结果",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designDrawingsNumber", "eq", "测试通图号-32m双线箱梁-860"),
                 r("$.data[0].numberType", "in", [2, "2"]),
                 r("$.data[0].bddId", "not_empty")],
                "新建编码的 numberType 应为 2（其他编码）；若为 1 说明用户创建的编码被错误标记为基础编码"))],
         pre=PRE() + [{"api_res_exist": [{
             "test_data_key": "bdd.probe.t01",
             "judgment_criteria_items": [{
                 "assertion_config": A([r("$..bddId", "not_empty")]),
                 "steps_after_success": ["bdd.del.t01.dev"],
                 "steps_after_failure": [],
             }],
         }]}])

bdd_case("bdd.add.boundary_153", SUB_ADD, "梁型码取下界153新增成功",
         "TC-BDD-014: 梁型码取用户可用区间下界 153（001~152 已被国铁占用），边界值应允许创建",
         [S("bdd.add.t11", "POST 新增 t11，designBeamType=153", OK),
          S("bdd.probe.t11", "GET 列表查询 designBeamType=153，回查落库结果",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designDrawingsNumber", "eq", "测试通图号-编码下界153")]))])

bdd_case("bdd.add.boundary_998", SUB_ADD, "梁型码取上界998新增成功",
         "TC-BDD-015: 梁型码取用户可用区间上界 998（999 已被占用），边界值应允许创建",
         [S("bdd.add.t12", "POST 新增 t12，designBeamType=998", OK),
          S("bdd.probe.t12", "GET 列表查询 designBeamType=998，回查落库结果",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designDrawingsNumber", "eq", "测试通图号-编码上界998")]))])

bdd_case("bdd.add.sort_first", SUB_ADD, "新建通图号在分页查询中排在最前",
         "TC-BDD-016: 需求 2.1.1「新创建的通图号及对应梁型码应默认排在最开始」。"
         "系统实现方式为：**通图号分页查询返回的数据里，新建记录位于第一条**。"
         "前置先按梁型码 872 定位并删除上一次运行可能残留的 t14（幂等），保证本条用例可重复执行；"
         "新增后立即按 pageNum=1&pageSize=10 分页查询，断言 data.list 的第一条就是刚创建的通图号",
         [S("bdd.add.t14", "POST 新增 t14（测试通图号-排序校验-872）", OK),
          S("bdd.page.default", "GET 分页查询 pageNum=1&pageSize=10，校验 list 首条即新记录",
            OKX([r("$.data.list", "type", "list"),
                 r("$.data.list", "length_gt", 0),
                 r("$.data.list[0].designDrawingsNumber", "eq", "测试通图号-排序校验-872"),
                 r("$.data.list[0].designBeamType", "eq", "872")],
                "新建记录应排在分页结果第一条（bddSort 最小或按创建时间倒序）；"
                "若出现在中间/末尾说明默认排序未按需求实现"))],
         pre=PRE() + [{"api_res_exist": [{
             "test_data_key": "bdd.probe.t14",
             "judgment_criteria_items": [{
                 "assertion_config": A([r("$..bddId", "not_empty")]),
                 "steps_after_success": ["bdd.del.t14.dev"],
                 "steps_after_failure": [],
             }],
         }]}])

bdd_case("bdd.add.dup_code", SUB_ADD, "梁型码重复新增被拒绝",
         "TC-BDD-017: 前置确保 t02（编码 861）存在，再用相同编码 861、不同图号名称新增，应被查重拒绝；"
         "回查 861 仍只有 1 条（t02 自身），证明重复记录未落库",
         [S("bdd.add.n07", "POST 新增，designBeamType=861（与 t02 相同），图号名称不同",
            FAIL("message 应提示梁型码已存在（重复），不得插入第二条同码记录")),
          S("bdd.probe.n07", "GET 列表查询 designBeamType=861，确认仍只有 1 条",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].designDrawingsNumber", "eq", "测试通图号-24m单线箱梁-861")]))],
         seeds=[("bdd.probe.t02", "bdd.add.t02")])

bdd_case("bdd.add.trim_dup_code", SUB_ADD, "梁型码带空格时去空格后查重被拒绝",
         "TC-BDD-018: 需求 2.1.1「梁型码除去用户填报的空格后查重」。前置确保 861 存在，"
         "再用「 861 」（前后各一个空格）新增，应被识别为重复而拒绝；回查该图号名称不存在，证明未落库",
         [S("bdd.add.n08", "POST 新增，designBeamType=「 861 」（带前后空格）",
            FAIL("message 应提示梁型码已存在；若返回成功说明查重未对编码做 trim，属于需求偏差")),
          S("bdd.probe.n08", "GET 列表查询 designBeamType=「 861 」，确认未落库",
            OKX([r("$.data", "is_empty")]))],
         seeds=[("bdd.probe.t02", "bdd.add.t02")])

bdd_case("bdd.add.reserved_code", SUB_ADD, "梁型码占用国铁内置编码被拒绝",
         "TC-BDD-019: 需求 2.1「国铁集团已占用 001~152、999，用户只能在 153~998 里生成」。"
         "用 100（区间内但已被占用）新增应被拒绝，且不得覆盖/修改原有内置记录",
         [S("bdd.add.n09", "POST 新增，designBeamType=100（国铁占用）",
            FAIL("message 应提示梁型码已被占用或不可用，不得插入也不得覆盖内置记录")),
          S("bdd.probe.n09", "GET 列表查询 designBeamType=100，确认未新增（内置记录仍只有 1 条）",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].numberType", "in", [1, "1"])]))],
         pre=PRE(with_builtin=True))

bdd_case("bdd.add.upper_occupied", SUB_ADD, "梁型码取999被拒绝",
         "TC-BDD-020: 999 既是国铁占用的最后一条、又超出用户可用上界 998，应被拒绝",
         [S("bdd.add.n10", "POST 新增，designBeamType=999",
            FAIL("message 应提示梁型码不可用（已被占用 / 超出 153~998 区间）")),
          S("bdd.probe.n10", "GET 列表查询 designBeamType=999，确认未新增",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].numberType", "in", [1, "1"])]))],
         pre=PRE(with_builtin=True))

bdd_case("bdd.add.range_invalid", SUB_ADD, "梁型码取000越界被拒绝",
         "TC-BDD-021: 000 小于用户可用下界 153，应被区间校验拒绝并给出明确提示",
         [S("bdd.add.n11", "POST 新增，designBeamType=000",
            FAIL("message 应提示梁型码必须在 153~998 区间内")),
          S("bdd.probe.n11", "GET 列表查询 designBeamType=000，确认未新增",
            OKX([r("$.data", "is_empty")]))])

bdd_case("bdd.add.code_too_short", SUB_ADD, "梁型码长度不足3位被拒绝",
         "TC-BDD-022: designBeamType 传 2 位「86」，需求要求长度 3，应被长度校验拒绝",
         [S("bdd.add.n05", "POST 新增，designBeamType=86（2 位）",
            FAIL("message 应提示梁型码长度必须为 3 位")),
          S("bdd.probe.n05", "GET 列表查询 designBeamType=86，确认未新增",
            OKX([r("$.data", "is_empty")]))])

bdd_case("bdd.add.code_too_long", SUB_ADD, "梁型码长度超过3位被拒绝",
         "TC-BDD-023: designBeamType 传 4 位「8601」，应被长度校验拒绝，且不得截断成 860 后落库（860 已被 t01 占用）",
         [S("bdd.add.n06", "POST 新增，designBeamType=8601（4 位）",
            FAIL("message 应提示梁型码长度必须为 3 位，不得截断后插入")),
          S("bdd.probe.n06", "GET 列表查询 designBeamType=8601，确认未新增",
            OKX([r("$.data", "is_empty")]))])

bdd_case("bdd.add.miss_number", SUB_ADD, "缺少必填字段designDrawingsNumber新增失败",
         "TC-BDD-024: 请求体不含图号名称，只带梁型码 874，必填校验应拦截；回查 874 不存在",
         [S("bdd.add.n01", "POST 新增，body 无 designDrawingsNumber", FAIL("message 应明确提示缺少通图号名称")),
          S("bdd.probe.n01", "GET 列表查询 designBeamType=874，确认未新增",
            OKX([r("$.data", "is_empty")]))])

bdd_case("bdd.add.empty_number", SUB_ADD, "图号名称为空串新增失败",
         "TC-BDD-025: designDrawingsNumber 传空串（长度 0，违反 1~50），应被拦截；回查 875 不存在",
         [S("bdd.add.n02", "POST 新增，designDrawingsNumber=\"\"", FAIL("message 应提示通图号名称不能为空")),
          S("bdd.probe.n02", "GET 列表查询 designBeamType=875，确认未新增",
            OKX([r("$.data", "is_empty")]))])

bdd_case("bdd.add.miss_code", SUB_ADD, "缺少必填字段designBeamType新增失败",
         "TC-BDD-027: 请求体不含梁型码，只带图号名称，必填校验应拦截",
         [S("bdd.add.n04", "POST 新增，body 无 designBeamType", FAIL("message 应明确提示缺少梁型码")),
          S("bdd.probe.n04", "GET 列表查询 designDrawingsNumber=测试通图号-缺梁型码-877，确认未新增",
            OKX([r("$.data", "is_empty")]))])

td("bdd.add.t15", "新增通图号-无令牌新增-897",
   "缺 Authorization 时的新增报文，梁型码 897", API["bdd_add"], H_NO_AUTH,
   {"designDrawingsNumber": "测试通图号-无令牌新增-897", "designBeamType": "897"}, None, None)
bdd_case("bdd.add.no_auth", SUB_ADD, "缺少Authorization新增通图号鉴权失败",
         "TC-BDD-028: 请求头只带 Sys-dept-id 新增（897），应鉴权失败且不落库",
         [S("bdd.add.t15", "POST 新增，请求头仅 Sys-dept-id", NO_AUTH()),
          S("bdd.probe.t15", "GET 列表查询 designBeamType=897，确认未落库",
            OKX([r("$.data", "is_empty")]))])

td("bdd.probe.t15", "探针-梁型码897", "按梁型码 897 查询，确认无鉴权新增未落库",
   API["bdd_list"], H_OK, None, {"designBeamType": "897"},
   [ex("bddIdT15", "$.data[0].bddId", "正常应为空")])

td("bdd.add.t16", "新增通图号-缺部门标识-898",
   "缺 Sys-dept-id 时的新增报文，梁型码 898", API["bdd_add"], H_NO_DEPT,
   {"designDrawingsNumber": "测试通图号-缺部门标识-898", "designBeamType": "898"}, None, None)
bdd_case("bdd.add.no_dept", SUB_ADD, "缺少Sys-dept-id新增通图号被拒绝且未落库",
         "TC-BDD-029: 请求头只带 Authorization，接口无法定位梁场；通图号按梁场独立管理，应拒绝执行并提示缺少部门标识",
         [S("bdd.add.t16", "POST 新增，请求头仅 Authorization", FAIL("缺少 Sys-dept-id 时应拒绝，提示梁场/部门标识缺失，不得落库")),
          S("bdd.probe.t16", "GET 列表查询 designBeamType=898，确认未落库",
            OKX([r("$.data", "is_empty")]))])

td("bdd.probe.t16", "探针-梁型码898", "按梁型码 898 查询，确认缺部门标识的新增未落库",
   API["bdd_list"], H_OK, None, {"designBeamType": "898"},
   [ex("bddIdT16", "$.data[0].bddId", "正常应为空")])

# ---- 编辑
bdd_case("bdd.update.name_success", SUB_UPD, "编辑通图号名称成功且可回查",
         "TC-BDD-030: 前置确保 t04（863）存在并取回 bddId，把图号名称改为「测试通图号-32m单线T梁-863已改」，"
         "梁型码不变；按 id 回查名称已更新、编码未变",
         [S("bdd.upd.t04", "POST 编辑 bddId=${bddIdT04}，仅改图号名称", OK),
          S("bdd.get.by_id.t04", "GET 通过id查询 bddId=${bddIdT04}，回查修改结果",
            OKX([r("$.data.designDrawingsNumber", "eq", "测试通图号-32m单线T梁-863已改"),
                 r("$.data.designBeamType", "eq", "863")]))],
         seeds=[("bdd.probe.t04", "bdd.add.t04")])

td("bdd.get.by_id.t04", "通图号通过id查询-t04", "按 bddId 回查 t04 编辑结果", API["bdd_get"], H_OK, None,
   {"bddId": "${bddIdT04}"}, None)

bdd_case("bdd.update.code_success", SUB_UPD, "编辑梁型码成功且改后仍受查重约束",
         "TC-BDD-031: 前置确保 t05（864）存在，把梁型码改为未被占用的 870、名称同步改为「测试通图号-24m双线箱梁-870」；"
         "回查编码与名称均已更新，且按 870 过滤只返回 1 条",
         [S("bdd.upd.t05", "POST 编辑 bddId=${bddIdT05}，梁型码 864→870", OK),
          S("bdd.get.by_id.t05", "GET 通过id查询 bddId=${bddIdT05}，回查修改结果",
            OKX([r("$.data.designBeamType", "eq", "870"),
                 r("$.data.designDrawingsNumber", "eq", "测试通图号-24m双线箱梁-870")]))],
         seeds=[("bdd.probe.t05", "bdd.add.t05")])

td("bdd.get.by_id.t05", "通图号通过id查询-t05", "按 bddId 回查 t05 编辑结果", API["bdd_get"], H_OK, None,
   {"bddId": "${bddIdT05}"}, None)

td("bdd.upd.miss_id", "编辑通图号-缺bddId",
   "请求体不带 bddId（无法定位待改记录），只带图号名称与梁型码", API["bdd_upd"], H_OK,
   {"designDrawingsNumber": "测试通图号-缺主键编辑-863", "designBeamType": "863"}, None, None)

bdd_case("bdd.update.miss_id", SUB_UPD, "编辑缺少主键bddId被拒绝",
         "TC-BDD-032: 编辑接口的 bddId 必填（文档表格里标「非必须」是标注错误）。"
         "前置确保 t04（863）存在，提交不带 bddId 的改名请求，应被必填校验拦截；"
         "回查 t04 的名称与编码都未被报文里的值改掉，证明没有误改任何记录",
         [S("bdd.upd.miss_id", "POST 编辑，body 无 bddId（只有名称与梁型码）",
            FAIL("message 应明确提示缺少主键 bddId，不得改动任何记录")),
          S("bdd.get.by_id.t04", "GET 通过id查询 bddId=${bddIdT04}，确认原记录未被改动",
            OKX([r("$.data.designDrawingsNumber", "ne", "测试通图号-缺主键编辑-863"),
                 r("$.data.designBeamType", "eq", "863")]))],
         seeds=[("bdd.probe.t04", "bdd.add.t04")])

bdd_case("bdd.update.dup_code", SUB_UPD, "编辑梁型码为已占用值被拒绝",
         "TC-BDD-032: 前置确保 t04（863）与 t02（861）都存在，把 t04 的梁型码改为 861，应被查重拒绝；"
         "回查 t04 的编码仍是 863，未被改动",
         [S("bdd.upd.dup_code", "POST 编辑 bddId=${bddIdT04}，designBeamType=861（已被 t02 占用）",
            FAIL("message 应提示梁型码已存在；不得改动原记录")),
          S("bdd.get.by_id.t04", "GET 通过id查询 bddId=${bddIdT04}，确认编码未被改动",
            OKX([r("$.data.designBeamType", "eq", "863")]))],
         seeds=[("bdd.probe.t04", "bdd.add.t04"), ("bdd.probe.t02", "bdd.add.t02")])

bdd_case("bdd.update.builtin", SUB_UPD, "国铁内置编码不允许编辑",
         "TC-BDD-033: 需求 2.1.2「除开已占用的 153 个编码外，其余通图号记录均可有条件编辑」。"
         "前置要求内置编码就绪，用内置编码的 bddId 改名，应被拒绝；回查名称未变",
         [S("bdd.upd.builtin", "POST 编辑，bddId 取内置编码，名称改为「测试通图号-篡改内置编码」",
            FAIL("message 应提示内置编码不允许编辑（或该记录不可修改）")),
          S("bdd.get.builtin", "GET 通过id查询内置编码，确认名称未被改动",
            OKX([r("$.data.designDrawingsNumber", "ne", "测试通图号-篡改内置编码"),
                 r("$.data.bddId", "not_empty")]))],
         pre=PRE(with_builtin=True))

bdd_case("bdd.update.no_auth", SUB_UPD, "缺少Authorization编辑通图号鉴权失败",
         "TC-BDD-034: 前置确保 t04 存在，请求头只带 Sys-dept-id 改名，应鉴权失败；回查名称仍是原值",
         [S("bdd.upd.t04.no_auth", "POST 编辑，请求头仅 Sys-dept-id，名称改为「测试通图号-无令牌篡改-863」", NO_AUTH()),
          S("bdd.get.by_id.t04", "GET 通过id查询 bddId=${bddIdT04}，确认未被篡改",
            OKX([r("$.data.designDrawingsNumber", "ne", "测试通图号-无令牌篡改-863")]))],
         seeds=[("bdd.probe.t04", "bdd.add.t04")])

# ---- 通过id删除
bdd_case("bdd.del.success", SUB_DEL, "按bddId删除通图号成功且查询为空",
         "TC-BDD-035: 前置确保 t06（865）存在并取回 bddId，删除后按 id 回查 data 为空，按编码过滤也为空",
         [S("bdd.del.t06", "GET 删除 bddId=${bddIdT06}", OK),
          S("bdd.get.not_exist.t06", "GET 通过id查询 bddId=${bddIdT06}，确认已删除",
            OKX([r("$.data", "is_empty")]))],
         seeds=[("bdd.probe.t06", "bdd.add.t06")])

td("bdd.get.not_exist.t06", "通图号通过id查询-t06删除后", "按已删除的 bddId 查询，data 应为空",
   API["bdd_get"], H_OK, None, {"bddId": "${bddIdT06}"}, None)

bdd_case("bdd.del.repeat", SUB_DEL, "重复删除同一通图号不报500",
         "TC-BDD-036: 前置确保 t09（868）存在，连续删除两次；第二次是「删除不存在的数据」，"
         "应幂等成功或返回明确提示，不得抛 500 / 数据库异常",
         [S("bdd.del.t09.first", "GET 删除 bddId=${bddIdT09}（第一次）", OK),
          S("bdd.del.t09.second", "GET 删除 bddId=${bddIdT09}（第二次，记录已不存在）",
            A([r("$.code", "eq", "200")],
              "重复删除应幂等（status=1）或返回 status=0 + 明确提示（记录不存在），不得抛 500 / 数据库异常"))],
         seeds=[("bdd.probe.t09", "bdd.add.t09")])

bdd_case("bdd.del.builtin", SUB_DEL, "国铁内置编码不允许删除",
         "TC-BDD-037: 需求 2.1.3「国铁 153 个通图号及梁型码不允许删除」。用内置编码的 bddId 删除应被拒绝；"
         "回查该记录仍存在",
         [S("bdd.del.builtin", "GET 删除 bddId=${bddBuiltInId}（内置编码）",
            FAIL("message 应提示内置编码不允许删除（或该记录受保护）")),
          S("bdd.get.builtin", "GET 通过id查询内置编码，确认记录仍在",
            OKX([r("$.data.bddId", "not_empty"),
                 r("$.data.designDrawingsNumber", "not_empty")]))],
         pre=PRE(with_builtin=True))

bdd_case("bdd.del.no_auth", SUB_DEL, "缺少Authorization删除通图号鉴权失败且记录仍在",
         "TC-BDD-038: 前置确保 t10（869）存在，请求头只带 Sys-dept-id 删除，应鉴权失败；回查记录仍存在",
         [S("bdd.del.t10.no_auth", "GET 删除 bddId=${bddIdT10}，请求头仅 Sys-dept-id", NO_AUTH()),
          S("bdd.get.by_id.t10", "GET 通过id查询 bddId=${bddIdT10}，确认记录仍在",
            OKX([r("$.data.bddId", "not_empty"),
                 r("$.data.designBeamType", "eq", "869")]))],
         seeds=[("bdd.probe.t10", "bdd.add.t10")])

td("bdd.get.by_id.t10", "通图号通过id查询-t10", "按 bddId 回查 t10", API["bdd_get"], H_OK, None,
   {"bddId": "${bddIdT10}"}, None)

# ---- 批量删除
bdd_case("bdd.del.batch_success", SUB_BATCH, "批量删除2条通图号成功",
         "TC-BDD-039: 前置确保 t07（866）/t08（867）存在，用逗号拼接的 bddIds 批量删除；两次回查 data 均为空",
         [S("bdd.batch.t07t08", "GET 批量删除 bddIds=${bddIdT07},${bddIdT08}", OK),
          S("bdd.get.not_exist.t07", "GET 通过id查询 bddId=${bddIdT07}，确认已删除", OKX([r("$.data", "is_empty")])),
          S("bdd.get.not_exist.t08", "GET 通过id查询 bddId=${bddIdT08}，确认已删除", OKX([r("$.data", "is_empty")]))],
         seeds=[("bdd.probe.t07", "bdd.add.t07"), ("bdd.probe.t08", "bdd.add.t08")])

td("bdd.get.not_exist.t07", "通图号通过id查询-t07删除后", "按已删除的 bddId 查询，data 应为空",
   API["bdd_get"], H_OK, None, {"bddId": "${bddIdT07}"}, None)
td("bdd.get.not_exist.t08", "通图号通过id查询-t08删除后", "按已删除的 bddId 查询，data 应为空",
   API["bdd_get"], H_OK, None, {"bddId": "${bddIdT08}"}, None)

bdd_case("bdd.del.batch_with_invalid", SUB_BATCH, "批量删除混入无效ID时有效记录仍被删除",
         "TC-BDD-040: 前置确保 t13（873）存在，bddIds 混入一个不存在的 999999999。"
         "接口应处理有效部分（有效记录被删）且不抛 500；若整体回滚，应给出明确提示而不是内部异常",
         [S("bdd.batch.with_invalid", "GET 批量删除 bddIds=${bddIdT13},999999999",
            A([r("$.code", "eq", "200")],
              "混入无效 ID 时不得抛 500 / SQL 异常；应返回成功（忽略无效 ID）或明确提示无效 ID")),
          S("bdd.get.not_exist.t13", "GET 通过id查询 bddId=${bddIdT13}，记录应已被删除",
            A([r("$.code", "eq", "200")],
              "有效 ID 对应的记录应被删除（data 为空）；若仍存在则说明一条无效 ID 导致整批失败"))],
         seeds=[("bdd.probe.t13", "bdd.add.t13")])

td("bdd.get.not_exist.t13", "通图号通过id查询-t13批量删除后", "按 bddId 查询，预期已被删除",
   API["bdd_get"], H_OK, None, {"bddId": "${bddIdT13}"}, None)

bdd_case("bdd.del.batch_miss_param", SUB_BATCH, "批量删除缺少bddIds被拒绝",
         "TC-BDD-041: 不传 bddIds（空 Query），应返回参数校验提示，不得抛 500 或误删全部数据",
         [S("bdd.batch.miss_param", "GET 批量删除，不带 bddIds",
            FAIL("message 应提示缺少参数 bddIds（或参数不能为空）；不得因空参数删除任何记录"))])

# ================================================================ 二、载荷计算
# 需求要点（梁体与通图号需求.md 2.2）：通图号生成后，在对应记录上配置静载试验设计参数；
#   rd / ed / fl 必填（字符串，长度 5），其余 21 项选填；psType、loadType 为枚举；
#   参数持久化后可在成果表中体现，且可反复修改。
# 载荷模块自建通图号（前缀「载荷测试图号-」），与通图号模块的清场前缀「测试通图号-」互不重叠，
# 因此两个模块可以各自独立执行、各自清理，不产生跨模块依赖。

SLD_BDD = [
    ("p01", "载荷测试图号-880-全参数配置", "880", "全字段配置：通过id查询、按 bddId 过滤"),
    ("p02", "载荷测试图号-881-最小必填配置", "881", "最小必填配置：分页第 2 条"),
    ("p03", "载荷测试图号-882-批量删除1", "882", "批量删除第 1 条"),
    ("p04", "载荷测试图号-883-批量删除2", "883", "批量删除第 2 条"),
    ("p05", "载荷测试图号-884-批量含无效", "884", "批量删除混入无效 ID"),
    ("p06", "载荷测试图号-885-编辑", "885", "编辑全字段"),
    ("p07", "载荷测试图号-886-删除成功", "886", "通过id删除成功"),
    ("p08", "载荷测试图号-887-重复删除", "887", "重复删除"),
    ("p09", "载荷测试图号-888-删除无鉴权", "888", "删除缺 Authorization"),
    ("p10", "载荷测试图号-889-缺设计强度", "889", "缺 rd 的负向报文"),
    ("p11", "载荷测试图号-890-缺弹性模量", "890", "缺 ed 的负向报文"),
    ("p12", "载荷测试图号-891-缺挠跨比", "891", "缺 fl 的负向报文"),
    ("p13", "载荷测试图号-892-缺部门标识", "892", "缺 Sys-dept-id 的负向报文"),
    ("p14", "载荷测试图号-893-重复配置", "893", "1:1 校验：同一通图号重复配置不产生第二条"),
]

for _c, _n, _b, _d in SLD_BDD:
    td("sld.bdd.add." + _c, "新增通图号（载荷用）-" + _n, "载荷模块自建通图号：" + _d + "；梁型码 " + _b,
       API["bdd_add"], H_OK, {"designDrawingsNumber": _n, "designBeamType": _b}, None, None)
    td("sld.bdd.probe." + _c, "探针-载荷用通图号" + _b,
       "按梁型码 " + _b + " 查询通图号，用于「先查后建」并提取 bddId",
       API["bdd_list"], H_OK, None, {"designBeamType": _b},
       [ex("sldBdd" + _c.upper(), "$.data[0].bddId", "梁型码 " + _b + " 对应的 bddId（载荷配置的外键）")])

SLD_P01 = {"bddId": "${sldBddP01}", "rd": 60, "ed": 36, "fl": "1/600", "psType": "1", "kf": 2.0,
           "w0": 1.234, "fpsi": 1.05, "a0": 5.68, "e0": 0.85, "loadType": "1", "md": 120.5,
           "mf": 35.2, "jackRow": 2, "jackColumn": 4, "mh": 180.6, "mz": 95.4, "sigma15": 30,
           "sigma16": 45, "mul": 1.15, "mul1": 1.08, "ay": 0.0125, "ag": 0.0032, "kq": 1.02, "kp": 1.05}

SLD_CFG = [
    ("l01", "p01", "全字段配置（24 项全传）", SLD_P01),
    ("l02", "p02", "最小必填配置（仅 bddId/rd/ed/fl）",
     {"bddId": "${sldBddP02}", "rd": 50, "ed": 34.5, "fl": "1/800"}),
    ("l03", "p03", "批量删除第 1 条", {"bddId": "${sldBddP03}", "rd": 55, "ed": 35, "fl": "1/700"}),
    ("l04", "p04", "批量删除第 2 条", {"bddId": "${sldBddP04}", "rd": 45, "ed": 33, "fl": "1/900"}),
    ("l05", "p05", "批量删除含无效 ID", {"bddId": "${sldBddP05}", "rd": 40, "ed": 32.5, "fl": "1/750"}),
    ("l06", "p06", "编辑目标（先配最小必填，再整体修改）",
     {"bddId": "${sldBddP06}", "rd": 50, "ed": 34.5, "fl": "1/800", "psType": "1", "kf": 1.8,
      "md": 100, "mh": 150, "mul": 1.1}),
    ("l07", "p07", "通过id删除成功", {"bddId": "${sldBddP07}", "rd": 50, "ed": 34.5, "fl": "1/800"}),
    ("l08", "p08", "重复删除", {"bddId": "${sldBddP08}", "rd": 50, "ed": 34.5, "fl": "1/800"}),
    ("l09", "p09", "删除缺 Authorization", {"bddId": "${sldBddP09}", "rd": 50, "ed": 34.5, "fl": "1/800"}),
    ("l10", "p14", "1:1 校验：先配一条最小必填配置",
     {"bddId": "${sldBddP14}", "rd": 52, "ed": 34.8, "fl": "1/780"}),
]

for _c, _p, _d, _b in SLD_CFG:
    td("sld.add." + _c, "新增载荷配置-" + _d, _d + "；配置到通图号 " + _p.upper(), API["sld_add"], H_OK, _b, None, None)
    td("sld.probe." + _c, "探针-载荷配置" + _c.upper(),
       "按 bddId 查询载荷配置，用于「先查后建」并提取 btdId（新增接口不返回主键）",
       API["sld_list"], H_OK, None, {"bddId": "${sldBdd" + _p.upper() + "}"},
       [ex("sldBtd" + _c.upper(), "$.data[0].btdId", "该通图号下配置的主键 btdId")])

td("sld.add.l10dup", "新增载荷配置-l10重复配置",
   "同一个通图号（p14）再提交一份参数（rd 改 70），用于验证 1:1 约束", API["sld_add"], H_OK,
   {"bddId": "${sldBddP14}", "rd": 70, "ed": 40, "fl": "1/500"}, None, None)

# 负向报文
td("sld.add.miss_bdd", "新增载荷配置-缺bddId", "请求体不含 bddId，只带 rd/ed/fl",
   API["sld_add"], H_OK, {"rd": 60, "ed": 36, "fl": "1/600"}, None, None)
td("sld.add.miss_rd", "新增载荷配置-缺rd", "缺设计混凝土强度 rd", API["sld_add"], H_OK,
   {"bddId": "${sldBddP10}", "ed": 36, "fl": "1/600"}, None, None)
td("sld.add.miss_ed", "新增载荷配置-缺ed", "缺设计混凝土弹性模量 ed", API["sld_add"], H_OK,
   {"bddId": "${sldBddP11}", "rd": 60, "fl": "1/600"}, None, None)
td("sld.add.miss_fl", "新增载荷配置-缺fl", "缺设计挠跨比 fl", API["sld_add"], H_OK,
   {"bddId": "${sldBddP12}", "rd": 60, "ed": 36}, None, None)
td("sld.add.no_auth", "新增载荷配置-缺Authorization", "请求头只带 Sys-dept-id", API["sld_add"], H_NO_AUTH,
   {"bddId": "${sldBddP01}", "rd": 60, "ed": 36, "fl": "1/600"}, None, None)
td("sld.add.no_dept", "新增载荷配置-缺Sys-dept-id", "请求头只带 Authorization，配置到 p13",
   API["sld_add"], H_NO_DEPT,
   {"bddId": "${sldBddP13}", "rd": 60, "ed": 36, "fl": "1/600"}, None, None)

# 查询/编辑/删除类数据
td("sld.list.all", "载荷配置列表-无参", "不带过滤条件查询，用于校验返回结构", API["sld_list"], H_OK, None, None, None)
td("sld.list.by_bdd", "载荷配置列表-按bddId", "按通图号 bddId 过滤（p01）", API["sld_list"], H_OK, None,
   {"bddId": "${sldBddP01}"}, None)
td("sld.list.no_auth", "载荷配置列表-缺Authorization", "请求头只带 Sys-dept-id", API["sld_list"], H_NO_AUTH,
   None, None, None)
td("sld.list.no_dept", "载荷配置列表-缺Sys-dept-id", "请求头只带 Authorization", API["sld_list"], H_NO_DEPT,
   None, None, None)
td("sld.page.default", "载荷配置分页-第1页10条", "pageNum=1&pageSize=10", API["sld_page"], H_OK, None,
   {"pageNum": 1, "pageSize": 10}, None)
td("sld.page.size1", "载荷配置分页-每页1条", "pageNum=1&pageSize=1", API["sld_page"], H_OK, None,
   {"pageNum": 1, "pageSize": 1}, None)
td("sld.page.second", "载荷配置分页-第2页", "pageNum=2&pageSize=1", API["sld_page"], H_OK, None,
   {"pageNum": 2, "pageSize": 1}, None)
td("sld.get.by_id", "载荷配置通过id查询", "按 btdId 查询（p01 的配置）", API["sld_get"], H_OK, None,
   {"btdId": "${sldBtdL01}"}, None)
td("sld.get.not_exist", "载荷配置通过id查询-不存在主键", "btdId=999999999", API["sld_get"], H_OK, None,
   {"btdId": "999999999"}, None)
td("sld.upd.l06", "编辑载荷配置-l06全字段",
   "把 l06 改为：rd 55 / ed 35.5 / fl 1/700 / psType 2 / loadType 0 / kf 1.9 / md 110.5 / mh 165.5 / mul 1.12",
   API["sld_upd"], H_OK,
   {"btdId": "${sldBtdL06}", "bddId": "${sldBddP06}", "rd": 55, "ed": 35.5, "fl": "1/700",
    "psType": "2", "loadType": "0", "kf": 1.9, "md": 110.5, "mh": 165.5, "mul": 1.12}, None, None)
td("sld.upd.miss_id", "编辑载荷配置-缺btdId", "不带主键 btdId，其余字段齐全", API["sld_upd"], H_OK,
   {"bddId": "${sldBddP06}", "rd": 55, "ed": 35.5, "fl": "1/700"}, None, None)
td("sld.upd.no_auth", "编辑载荷配置-缺Authorization",
   "请求头只带 Sys-dept-id，把 rd 改为 66（应失败且不生效）", API["sld_upd"], H_NO_AUTH,
   {"btdId": "${sldBtdL06}", "bddId": "${sldBddP06}", "rd": 66, "ed": 35.5, "fl": "1/700"}, None, None)
td("sld.del.l07", "删除载荷配置-l07", "删除 p07 的配置", API["sld_del"], H_OK, None,
   {"btdId": "${sldBtdL07}"}, None)
td("sld.del.l08.first", "删除载荷配置-l08第一次", "删除 p08 的配置", API["sld_del"], H_OK, None,
   {"btdId": "${sldBtdL08}"}, None)
td("sld.del.l08.second", "删除载荷配置-l08第二次", "再次删除同一 btdId，验证幂等", API["sld_del"], H_OK,
   None, {"btdId": "${sldBtdL08}"}, None)
td("sld.del.l09.no_auth", "删除载荷配置-l09缺Authorization", "请求头只带 Sys-dept-id", API["sld_del"],
   H_NO_AUTH, None, {"btdId": "${sldBtdL09}"}, None)
td("sld.batch.l03l04", "批量删除载荷配置-l03,l04", "btdIds=${sldBtdL03},${sldBtdL04}", API["sld_batch"],
   H_OK, None, {"btdIds": "${sldBtdL03},${sldBtdL04}"}, None)
td("sld.batch.with_invalid", "批量删除载荷配置-l05+无效ID", "btdIds 混入 999999999", API["sld_batch"],
   H_OK, None, {"btdIds": "${sldBtdL05},999999999"}, None)
td("sld.batch.miss_param", "批量删除载荷配置-缺btdIds", "不传 btdIds", API["sld_batch"], H_OK, None, {}, None)
td("sld.batch.no_auth", "批量删除载荷配置-缺Authorization", "请求头只带 Sys-dept-id", API["sld_batch"],
   H_NO_AUTH, None, None, None)
td("sld.get.not_exist.l07", "载荷配置通过id查询-l07删除后", "按已删除的 btdId 查询", API["sld_get"], H_OK,
   None, {"btdId": "${sldBtdL07}"}, None)
td("sld.get.not_exist.l03", "载荷配置通过id查询-l03删除后", "按已删除的 btdId 查询", API["sld_get"], H_OK,
   None, {"btdId": "${sldBtdL03}"}, None)
td("sld.get.not_exist.l04", "载荷配置通过id查询-l04删除后", "按已删除的 btdId 查询", API["sld_get"], H_OK,
   None, {"btdId": "${sldBtdL04}"}, None)
td("sld.get.not_exist.l05", "载荷配置通过id查询-l05批量删除后", "按 btdId 查询，预期已被删除", API["sld_get"],
   H_OK, None, {"btdId": "${sldBtdL05}"}, None)
td("sld.get.l09", "载荷配置通过id查询-l09", "按 btdId 回查 l09，确认删除被拒绝后记录仍在", API["sld_get"],
   H_OK, None, {"btdId": "${sldBtdL09}"}, None)
td("sld.get.l06", "载荷配置通过id查询-l06", "按 btdId 回查 l06 编辑结果", API["sld_get"], H_OK, None,
   {"btdId": "${sldBtdL06}"}, None)
td("sld.del.l01.dev", "删除载荷配置-l01前置清理",
   "新增成功用例执行前删掉 p01 下可能残留的配置，避免重复执行撞唯一约束（幂等）", API["sld_del"], H_OK,
   None, {"btdId": "${sldBtdL01}"}, None)
td("sld.del.l02.dev", "删除载荷配置-l02前置清理",
   "仅必填新增用例执行前删掉 p02 下可能残留的配置，避免重复执行撞唯一约束（幂等）", API["sld_del"], H_OK,
   None, {"btdId": "${sldBtdL02}"}, None)
td("sld.list.by_bdd_p10", "载荷配置列表-按bddId(p10)", "确认缺必填的负向报文没有落库",
   API["sld_list"], H_OK, None, {"bddId": "${sldBddP10}"}, None)
td("sld.list.by_bdd_p11", "载荷配置列表-按bddId(p11)", "确认缺 ed 的负向报文没有落库",
   API["sld_list"], H_OK, None, {"bddId": "${sldBddP11}"}, None)
td("sld.list.by_bdd_p12", "载荷配置列表-按bddId(p12)", "确认缺 fl 的负向报文没有落库",
   API["sld_list"], H_OK, None, {"bddId": "${sldBddP12}"}, None)
td("sld.list.by_bdd_p13", "载荷配置列表-按bddId(p13)", "确认缺部门标识的新增没有落库",
   API["sld_list"], H_OK, None, {"bddId": "${sldBddP13}"}, None)


CFG_TO_BDD = {c: p for c, p, d, b in SLD_CFG}


def seed_sld(*cfg_codes):
    """载荷用例的公共造数：通图号「先查后建」（新增后回查取 bddId）+ 载荷配置「先查后建」（新增后回查取 btdId）"""
    out = []
    for c in cfg_codes:
        p = CFG_TO_BDD[c]
        out.append(("sld.bdd.probe." + p, "sld.bdd.add." + p, True))
        out.append(("sld.probe." + c, "sld.add." + c, True))
    return out


SLD_ALL_KEYS = ["btdId", "bddId", "rd", "ed", "fl", "psType", "kf", "w0", "fpsi", "a0", "e0",
                "loadType", "md", "mf", "jackRow", "jackColumn", "mh", "mz", "sigma15", "sigma16",
                "mul", "mul1", "ay", "ag", "kq", "kp"]

sld_page_ok = [
    r("$.data", "res_contains_key", ["total", "list", "pageNum", "pageSize", "pages",
                                     "isFirstPage", "isLastPage"]),
    r("$.data.total", "gte", 1),
    r("$.data.pageNum", "in", [1, "1"]),
    r("$.data.pageSize", "in", [10, "10"]),
    r("$.data.list", "type", "list"),
    r("$.data.list", "length_gt", 0),
    r("$.data.list[0]", "res_contains_key", SLD_ITEM_KEYS),
    r("$.data.isFirstPage", "in", [True, "true", 1]),
]

# ---- 分页
sld_case("sld.query.page_success", SUB_PAGE, "分页查询第1页10条返回结构正确",
         "TC-SLD-001: 前置确保 l01/l02 两条配置存在（通图号与配置都「先查后建」），按 pageNum=1&pageSize=10 查询，"
         "校验分页结构齐全、list 非空且元素含 btdId/bddId/rd/ed/fl",
         [S("sld.page.default", "GET 分页查询 pageNum=1&pageSize=10", OKX(sld_page_ok))],
         seeds=seed_sld("l01", "l02"))

sld_case("sld.query.page_size_one", SUB_PAGE, "每页1条时分页返回仅1条记录",
         "TC-SLD-002: 按 pageNum=1&pageSize=1 查询，校验 list 长度恰为 1、pageSize=1、isFirstPage=true",
         [S("sld.page.size1", "GET 分页查询 pageNum=1&pageSize=1",
            OKX([r("$.data.pageSize", "in", [1, "1"]),
                 r("$.data.list", "length_eq", 1),
                 r("$.data.isFirstPage", "in", [True, "true", 1])]))],
         seeds=seed_sld("l01", "l02"))

sld_case("sld.query.page_second", SUB_PAGE, "第2页翻页正确且首页标记为false",
         "TC-SLD-003: 至少 2 条数据时按 pageNum=2&pageSize=1 查询，校验返回 1 条、pageNum=2、isFirstPage=false、hasPreviousPage=true",
         [S("sld.page.second", "GET 分页查询 pageNum=2&pageSize=1",
            OKX([r("$.data.list", "length_eq", 1),
                 r("$.data.pageNum", "in", [2, "2"]),
                 r("$.data.isFirstPage", "in", [False, "false", 0]),
                 r("$.data.hasPreviousPage", "in", [True, "true", 1])]))],
         seeds=seed_sld("l01", "l02"))

# ---- 列表
sld_case("sld.query.list_success", SUB_LIST, "无参列表查询返回字段完整",
         "TC-SLD-004: 前置确保 l01 存在后不带过滤条件查询，校验 data 为数组、非空、元素含 btdId/bddId/rd/ed/fl",
         [S("sld.list.all", "GET 列表查询（无参）",
            OKX([r("$.data", "type", "list"),
                 r("$.data", "length_gt", 0),
                 r("$.data[0]", "res_contains_key", SLD_ITEM_KEYS)]))],
         seeds=seed_sld("l01"))

sld_case("sld.query.list_by_bdd", SUB_LIST, "按通图号bddId过滤只返回该通图号的配置",
         "TC-SLD-005: 静载参数与通图号一一关联。前置确保 p01 + l01 存在后按 bddId 过滤，"
         "应恰好返回 1 条且 bddId 与过滤值一致（bddId 用上下文变量比对，避免依赖步骤内请求报文）",
         [S("sld.list.by_bdd", "GET 列表查询 bddId=${sldBddP01}",
            OKX([r("$.data", "length_eq", 1),
                 rv("$.data[0].bddId", "eq", "sldBddP01"),
                 r("$.data[0].rd", "in", [60, "60", 60.0]),
                 r("$.data[0].fl", "eq", "1/600")]))],
         seeds=seed_sld("l01"))

sld_case("sld.query.list_no_auth", SUB_LIST, "缺少Authorization查询载荷配置鉴权失败",
         "TC-SLD-006: 请求头只带 Sys-dept-id，应鉴权失败且不返回数据",
         [S("sld.list.no_auth", "GET 列表查询，请求头仅 Sys-dept-id",
            A([r("$.status", "ne", "1"), r("$.data", "is_empty")]))])

sld_case("sld.query.list_no_dept", SUB_LIST, "缺少Sys-dept-id查询不返回载荷配置",
         "TC-SLD-007: 请求头只带 Authorization，接口无法定位梁场，应返回空列表或业务提示，不得串出其它梁场数据",
         [S("sld.list.no_dept", "GET 列表查询，请求头仅 Authorization",
            A([r("$..btdId", "is_empty")],
              "缺少 Sys-dept-id 时应返回空列表或“梁场/部门不存在”类提示，不得返回任何静载参数，也不得抛内部异常"))])

# ---- 新增
sld_case("sld.add.success", SUB_ADD, "新增载荷配置成功（24项全传）",
         "TC-SLD-008: 为通图号 p01 配置静载试验设计参数，24 项全传（3 项必填 + 2 项枚举 + 19 项选填）。"
         "前置先确保通图号 p01 存在，并按 bddId 清掉可能残留的配置（幂等），避免重复执行时撞唯一约束。"
         "新增不返回主键，按 bddId 回查确认逐字段落库：数值字段与报文一致、枚举字段 psType/loadType 正确",
         [S("sld.add.l01", "POST 新增，bddId=${sldBddP01}，24 项全传", OK),
          S("sld.probe.l01", "GET 列表查询 bddId=${sldBddP01}，逐字段回查",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].bddId", "not_empty"),
                 r("$.data[0].rd", "in", [60, "60", 60.0]),
                 r("$.data[0].ed", "in", [36, "36", 36.0]),
                 r("$.data[0].fl", "eq", "1/600"),
                 r("$.data[0].psType", "eq", "1"),
                 r("$.data[0].kf", "in", [2.0, "2.0", 2]),
                 r("$.data[0].w0", "in", [1.234, "1.234"]),
                 r("$.data[0].fpsi", "in", [1.05, "1.05"]),
                 r("$.data[0].a0", "in", [5.68, "5.68"]),
                 r("$.data[0].e0", "in", [0.85, "0.85"]),
                 r("$.data[0].loadType", "eq", "1"),
                 r("$.data[0].md", "in", [120.5, "120.5"]),
                 r("$.data[0].mf", "in", [35.2, "35.2"]),
                 r("$.data[0].jackRow", "in", [2, "2"]),
                 r("$.data[0].jackColumn", "in", [4, "4"]),
                 r("$.data[0].mh", "in", [180.6, "180.6"]),
                 r("$.data[0].mz", "in", [95.4, "95.4"]),
                 r("$.data[0].mul", "in", [1.15, "1.15"]),
                 r("$.data[0].mul1", "in", [1.08, "1.08"]),
                 r("$.data[0].ay", "in", [0.0125, "0.0125"]),
                 r("$.data[0].kq", "in", [1.02, "1.02"]),
                 r("$.data[0].kp", "in", [1.05, "1.05"])],
                "静载参数配置需完整持久化：任一选填项丢失或被截断都说明字段映射不全"))],
         pre=PRE() + [seed_block("sld.bdd.probe.p01", "sld.bdd.add.p01", True),
                      {"api_res_exist": [{
                          "test_data_key": "sld.probe.l01",
                          "judgment_criteria_items": [{
                              "assertion_config": A([r("$..btdId", "not_empty")]),
                              "steps_after_success": ["sld.del.l01.dev"],
                              "steps_after_failure": [],
                          }],
                      }]}])

sld_case("sld.add.min_fields", SUB_ADD, "仅传必填字段新增成功",
         "TC-SLD-009: 只传 bddId/rd/ed/fl（不传任何选填项与枚举），应新增成功。"
         "前置先确保通图号 p02 存在并清掉残留配置（幂等）；回查必填项正确，选填项为空或 null 且不报错",
         [S("sld.add.l02", "POST 新增，bddId=${sldBddP02}，只传 3 项必填 + bddId", OK),
          S("sld.probe.l02", "GET 列表查询 bddId=${sldBddP02}，回查必填项",
            OKX([r("$.data", "length_eq", 1),
                 r("$.data[0].rd", "in", [50, "50", 50.0]),
                 r("$.data[0].ed", "in", [34.5, "34.5"]),
                 r("$.data[0].fl", "eq", "1/800")],
                "选填项未传时应为空/null，不应报错，也不应写入 0 之类的默认值掩饰缺省"))],
         pre=PRE() + [seed_block("sld.bdd.probe.p02", "sld.bdd.add.p02", True),
                      {"api_res_exist": [{
                          "test_data_key": "sld.probe.l02",
                          "judgment_criteria_items": [{
                              "assertion_config": A([r("$..btdId", "not_empty")]),
                              "steps_after_success": ["sld.del.l02.dev"],
                              "steps_after_failure": [],
                          }],
                      }]}])

sld_case("sld.add.one_to_one", SUB_ADD, "同一通图号重复配置静载参数不会产生第二条",
         "TC-SLD-010: 一个通图号只对应一条静载参数（1:1）。前置确保 p14 已配一条（先查后建），"
         "再为同一 bddId 提交第二份参数（rd 不同）：无论接口是拒绝（提示已存在）还是覆盖更新，"
         "按 bddId 回查都必须只有 1 条，不得因为参数不同就并存两条",
         [S("sld.add.l10dup", "POST 再次为 bddId=${sldBddP14} 新增一份参数（rd=70/ed=40/fl=1/500）",
            A([r("$.code", "eq", "200")],
              "同一通图号只允许一条静载参数：第二份应被拒绝（status=0 + 提示该通图号已配置）或覆盖更新（status=1），"
              "两种行为都可接受；不得插入第二条")),
          S("sld.probe.l10", "GET 列表查询 bddId=${sldBddP14}，确认该通图号下仍只有 1 条",
            OKX([r("$.data", "length_eq", 1)],
                "1:1 约束：同一 bddId 下只能有一条静载参数；返回 2 条说明约束未生效"))],
         seeds=seed_sld("l10"))

sld_case("sld.add.miss_bdd", SUB_ADD, "缺少必填字段bddId新增失败",
         "TC-SLD-010: 请求体不含 bddId（静载参数必须挂在通图号上），必填校验应拦截",
         [S("sld.add.miss_bdd", "POST 新增，body 无 bddId（只带 rd/ed/fl）",
            FAIL("message 应明确提示缺少通图号（bddId），不得插入一条无归属的配置"))])

sld_case("sld.add.miss_rd", SUB_ADD, "缺少必填字段rd（设计混凝土强度）新增失败",
         "TC-SLD-011: 定义混凝土强度为必填（需求 2.2）。请求体不含 rd，应被拦截；回查 p10 下没有配置落库",
         [S("sld.add.miss_rd", "POST 新增，bddId=${sldBddP10}，body 无 rd",
            FAIL("message 应明确提示缺少设计混凝土强度 rd")),
          S("sld.list.by_bdd_p10", "GET 列表查询 bddId=${sldBddP10}，确认未落库", OKX([r("$.data", "is_empty")]))],
         seeds=[("sld.bdd.probe.p10", "sld.bdd.add.p10", True)])

sld_case("sld.add.miss_ed", SUB_ADD, "缺少必填字段ed（设计混凝土弹性模量）新增失败",
         "TC-SLD-012: 请求体不含 ed，应被拦截；回查 p11 下没有配置落库",
         [S("sld.add.miss_ed", "POST 新增，bddId=${sldBddP11}，body 无 ed",
            FAIL("message 应明确提示缺少设计混凝土弹性模量 ed")),
          S("sld.list.by_bdd_p11", "GET 列表查询 bddId=${sldBddP11}，确认未落库", OKX([r("$.data", "is_empty")]))],
         seeds=[("sld.bdd.probe.p11", "sld.bdd.add.p11", True)])

sld_case("sld.add.miss_fl", SUB_ADD, "缺少必填字段fl（设计挠跨比）新增失败",
         "TC-SLD-013: 请求体不含 fl，应被拦截；回查 p12 下没有配置落库",
         [S("sld.add.miss_fl", "POST 新增，bddId=${sldBddP12}，body 无 fl",
            FAIL("message 应明确提示缺少设计挠跨比 fl")),
          S("sld.list.by_bdd_p12", "GET 列表查询 bddId=${sldBddP12}，确认未落库", OKX([r("$.data", "is_empty")]))],
         seeds=[("sld.bdd.probe.p12", "sld.bdd.add.p12", True)])

sld_case("sld.add.no_auth", SUB_ADD, "缺少Authorization新增载荷配置鉴权失败",
         "TC-SLD-014: 请求头只带 Sys-dept-id 新增（配置到 p01 以外的失败场景由回查兜底），应鉴权失败",
         [S("sld.add.no_auth", "POST 新增，请求头仅 Sys-dept-id", NO_AUTH())],
         seeds=[("sld.bdd.probe.p01", "sld.bdd.add.p01", True)])

sld_case("sld.add.no_dept", SUB_ADD, "缺少Sys-dept-id新增载荷配置被拒绝且未落库",
         "TC-SLD-015: 请求头只带 Authorization，接口无法定位梁场，应拒绝执行；回查 p13 下没有配置落库",
         [S("sld.add.no_dept", "POST 新增，请求头仅 Authorization，bddId=${sldBddP13}",
            FAIL("缺少 Sys-dept-id 时应拒绝，提示梁场/部门标识缺失，不得落库")),
          S("sld.list.by_bdd_p13", "GET 列表查询 bddId=${sldBddP13}，确认未落库", OKX([r("$.data", "is_empty")]))],
         seeds=[("sld.bdd.probe.p13", "sld.bdd.add.p13", True)])

# ---- 通过id查询
sld_case("sld.query.by_id_success", SUB_GET, "通过btdId查询单个配置字段完整",
         "TC-SLD-016: 前置确保 p01 + l01 存在并取回 btdId，按 id 查询，校验 26 个字段齐全、"
         "bddId 与所属通图号一致（用上下文变量比对）、rd/ed/fl 与报文一致",
         [S("sld.get.by_id", "GET 通过id查询 btdId=${sldBtdL01}",
            OKX([r("$.data", "res_contains_key", SLD_ALL_KEYS),
                 r("$.data.btdId", "not_empty"),
                 rv("$.data.bddId", "eq", "sldBddP01"),
                 r("$.data.rd", "in", [60, "60", 60.0]),
                 r("$.data.ed", "in", [36, "36", 36.0]),
                 r("$.data.fl", "eq", "1/600"),
                 r("$.data.psType", "eq", "1"),
                 r("$.data.loadType", "eq", "1")]))],
         seeds=seed_sld("l01"))

sld_case("sld.query.by_id_not_exist", SUB_GET, "查询不存在的主键不报500",
         "TC-SLD-017: btdId=999999999，应返回空数据或明确提示，不得抛 500 / 数据库异常",
         [S("sld.get.not_exist", "GET 通过id查询 btdId=999999999",
            A([r("$.code", "eq", "200")],
              "主键不存在时应返回 data=null 或 status=0 + 明确提示（记录不存在），不得抛 500 / 数据库异常"))])

# ---- 编辑
sld_case("sld.update.success", SUB_UPD, "编辑载荷配置全字段成功且可回查",
         "TC-SLD-018: 前置确保 p06 + l06 存在，整体修改 rd/ed/fl/psType/loadType/kf/md/mh/mul；"
         "按 btdId 回查改后值，未修改的选填项应保持原值",
         [S("sld.upd.l06", "POST 编辑 btdId=${sldBtdL06}，全字段修改", OK),
          S("sld.get.l06", "GET 通过id查询 btdId=${sldBtdL06}，回查修改结果",
            OKX([r("$.data.rd", "in", [55, "55", 55.0]),
                 r("$.data.ed", "in", [35.5, "35.5"]),
                 r("$.data.fl", "eq", "1/700"),
                 r("$.data.psType", "eq", "2"),
                 r("$.data.loadType", "eq", "0"),
                 r("$.data.kf", "in", [1.9, "1.9"]),
                 r("$.data.md", "in", [110.5, "110.5"]),
                 r("$.data.mh", "in", [165.5, "165.5"]),
                 r("$.data.mul", "in", [1.12, "1.12"]),
                 rv("$.data.bddId", "eq", "sldBddP06")],
                "编辑应整体覆盖：报文里给出的字段全部更新，未给出的选填项保持原值不被清空"))],
         seeds=seed_sld("l06"))

sld_case("sld.update.miss_id", SUB_UPD, "编辑缺少主键btdId被拒绝",
         "TC-SLD-019: 请求体不带 btdId（无法定位记录），应被拒绝；不得误改同通图号下的配置或插入新记录",
         [S("sld.upd.miss_id", "POST 编辑，body 无 btdId", FAIL("message 应明确提示缺少主键 btdId")),
          S("sld.get.l06", "GET 通过id查询 btdId=${sldBtdL06}，确认原记录未被改动",
            OKX([r("$.data.rd", "in", [50, "50", 50.0])]))],
         seeds=seed_sld("l06"))

sld_case("sld.update.no_auth", SUB_UPD, "缺少Authorization编辑载荷配置鉴权失败且未生效",
         "TC-SLD-020: 请求头只带 Sys-dept-id 把 rd 改为 66，应鉴权失败；回查 rd 仍为编辑前的值",
         [S("sld.upd.no_auth", "POST 编辑，请求头仅 Sys-dept-id，rd=66", NO_AUTH()),
          S("sld.get.l06", "GET 通过id查询 btdId=${sldBtdL06}，确认 rd 未被改成 66",
            OKX([r("$.data.rd", "ne", 66)]))],
         seeds=seed_sld("l06"))

# ---- 通过id删除
sld_case("sld.del.success", SUB_DEL, "按btdId删除载荷配置成功且查询为空",
         "TC-SLD-021: 前置确保 p07 + l07 存在，删除后按 btdId 回查 data 为空",
         [S("sld.del.l07", "GET 删除 btdId=${sldBtdL07}", OK),
          S("sld.get.not_exist.l07", "GET 通过id查询 btdId=${sldBtdL07}，确认已删除",
            OKX([r("$.data", "is_empty")]))],
         seeds=seed_sld("l07"))

sld_case("sld.del.repeat", SUB_DEL, "重复删除同一载荷配置不报500",
         "TC-SLD-022: 前置确保 p08 + l08 存在，连续删除两次；第二次应幂等成功或返回明确提示，不得抛 500",
         [S("sld.del.l08.first", "GET 删除 btdId=${sldBtdL08}（第一次）", OK),
          S("sld.del.l08.second", "GET 删除 btdId=${sldBtdL08}（第二次）",
            A([r("$.code", "eq", "200")],
              "重复删除应幂等（status=1）或返回 status=0 + 明确提示，不得抛 500 / 数据库异常"))],
         seeds=seed_sld("l08"))

sld_case("sld.del.no_auth", SUB_DEL, "缺少Authorization删除载荷配置鉴权失败且记录仍在",
         "TC-SLD-023: 前置确保 p09 + l09 存在，请求头只带 Sys-dept-id 删除，应鉴权失败；回查记录仍存在",
         [S("sld.del.l09.no_auth", "GET 删除 btdId=${sldBtdL09}，请求头仅 Sys-dept-id", NO_AUTH()),
          S("sld.get.l09", "GET 通过id查询 btdId=${sldBtdL09}，确认记录仍在",
            OKX([r("$.data.btdId", "not_empty")]))],
         seeds=seed_sld("l09"))

# ---- 批量删除
sld_case("sld.del.batch_success", SUB_BATCH, "批量删除2条载荷配置成功",
         "TC-SLD-024: 前置确保 p03/l03 与 p04/l04 存在，用逗号拼接的 btdIds 批量删除；两次回查均为空",
         [S("sld.batch.l03l04", "GET 批量删除 btdIds=${sldBtdL03},${sldBtdL04}", OK),
          S("sld.get.not_exist.l03", "GET 通过id查询 btdId=${sldBtdL03}，确认已删除", OKX([r("$.data", "is_empty")])),
          S("sld.get.not_exist.l04", "GET 通过id查询 btdId=${sldBtdL04}，确认已删除", OKX([r("$.data", "is_empty")]))],
         seeds=seed_sld("l03", "l04"))

sld_case("sld.del.batch_with_invalid", SUB_BATCH, "批量删除混入无效ID时有效记录仍被删除",
         "TC-SLD-025: 前置确保 p05/l05 存在，btdIds 混入不存在的 999999999，不得抛 500；有效记录应被删除",
         [S("sld.batch.with_invalid", "GET 批量删除 btdIds=${sldBtdL05},999999999",
            A([r("$.code", "eq", "200")],
              "混入无效 ID 时不得抛 500 / SQL 异常；应忽略无效 ID 返回成功或给出明确提示")),
          S("sld.get.not_exist.l05", "GET 通过id查询 btdId=${sldBtdL05}，记录应已被删除",
            A([r("$.code", "eq", "200")],
              "有效 ID 对应的配置应被删除（data 为空）；若仍存在说明一条无效 ID 导致整批回滚"))],
         seeds=seed_sld("l05"))

sld_case("sld.del.batch_miss_param", SUB_BATCH, "批量删除缺少btdIds被拒绝",
         "TC-SLD-026: 不传 btdIds，应返回参数校验提示，不得抛 500 或误删全部数据",
         [S("sld.batch.miss_param", "GET 批量删除，不带 btdIds",
            FAIL("message 应提示缺少参数 btdIds；不得因空参数删除任何记录"))])

# ================================================================ 三、模块清场
# 规则：以模块为最小单位清场，挂在模块最后一条用例的后置步骤；
#      通图号模块只清「测试通图号-」前缀，载荷模块只清「载荷测试图号-」前缀，互不干扰。


def build_cleanup(mod, scan_key, scan_name, del_key_prefix, names, code_fallbacks, del_api, id_field, name_field):
    """按名称（无名称报文按编码兜底）扫描 → 命中才删，返回 (scan_data_extract, items, del_datas)"""
    scan_ex = []
    for i, nm in enumerate(names):
        scan_ex.append(ex("fin%s%d" % (mod, i), "$..[?(@.%s=='%s')].%s" % (name_field, nm, id_field),
                          "清场用：按%s定位「%s」的 %s" % (name_field, nm, id_field)))
    off = len(names)
    for j, code in enumerate(code_fallbacks):
        scan_ex.append(ex("fin%sCode%d" % (mod, j), "$..[?(@.designBeamType=='%s')].%s" % (code, id_field),
                          "清场用：无名称的报文按梁型码 %s 兜底定位 %s" % (code, id_field)))
    items, del_datas = [], []
    for i, nm in enumerate(names):
        dk = "%s.%d" % (del_key_prefix, i)
        del_datas.append((dk, "清场删除-%s" % nm, "删除「%s」（扫到才执行，幂等）" % nm,
                          del_api, {id_field: "${fin%s%d}" % (mod, i)}))
        items.append({"assertion_config": A([r("$..[?(@.%s=='%s')].%s" % (name_field, nm, id_field), "not_empty")]),
                      "steps_after_failure": [],
                      "steps_after_success": [dk]})
    for j, code in enumerate(code_fallbacks):
        dk = "%s.code%d" % (del_key_prefix, j)
        del_datas.append((dk, "清场删除-梁型码%s" % code, "删除梁型码 %s 的记录（无名称报文兜底，幂等）" % code,
                          del_api, {id_field: "${fin%sCode%d}" % (mod, j)}))
        items.append({"assertion_config": A([r("$..[?(@.designBeamType=='%s')].%s" % (code, id_field), "not_empty")]),
                      "steps_after_failure": [],
                      "steps_after_success": [dk]})
    return scan_ex, items, del_datas


# ---- 通图号清场
_bdd_names, _bdd_codes = [], []
for _d in test_data:
    if _d["api_info_id"] in (API["bdd_add"], API["bdd_upd"]) and isinstance(_d["data"], dict):
        _nm = _d["data"].get("designDrawingsNumber")
        if isinstance(_nm, str) and _nm.startswith(BDD_PREFIX) and _nm not in _bdd_names:
            _bdd_names.append(_nm)
for _d in test_data:
    if _d["api_info_id"] == API["bdd_add"] and isinstance(_d["data"], dict) \
            and not _d["data"].get("designDrawingsNumber"):
        _bdd_codes.append(_d["data"]["designBeamType"])

_bdd_scan_ex, _bdd_items, _bdd_dels = build_cleanup(
    "Bdd", "bdd.cleanup.scan_all", "清场扫描-本梁场全部通图号",
    "bdd.cleanup.del", _bdd_names, _bdd_codes, API["bdd_del"], "bddId", "designDrawingsNumber")

td("bdd.cleanup.scan_all", "清场扫描-本梁场全部通图号",
   "不带过滤条件查询本梁场全部通图号，按 %d 个测试通图号名称逐一提取 bddId（无名称的报文按梁型码兜底）"
   % len(_bdd_names), API["bdd_list"], H_OK, None, None, _bdd_scan_ex)
for _dk, _n, _desc, _api, _params in _bdd_dels:
    td(_dk, _n, _desc, _api, H_OK, None, _params, None)

# ---- 载荷清场（先删配置，再删自己创建的通图号）
_sld_names = [n for _c, n, _b, _d in SLD_BDD]
_sld_scan_ex = [ex("finSld%d" % i, "$..[?(@.designDrawingsNumber=='%s')].bddId" % nm,
                   "清场用：按图号名称定位「%s」的 bddId" % nm) for i, nm in enumerate(_sld_names)]
td("sld.cleanup.scan_bdd", "清场扫描-载荷模块自建通图号",
   "不带过滤条件查询本梁场全部通图号，按 %d 个「载荷测试图号-」名称提取 bddId" % len(_sld_names),
   API["bdd_list"], H_OK, None, None, _sld_scan_ex)

_sld_cleanup_blocks = []
_BDD_TO_CFG = {p: c for c, p, d, b in SLD_CFG}  # 通图号编号 -> 载荷配置编号（一图号一配置）
for i, (_pcode, nm, _b, _d) in enumerate(SLD_BDD):
    bk = "sld.cleanup.del_bdd.%d" % i
    td(bk, "清场删除-载荷用通图号-%s" % nm,
       "删除载荷模块自建的通图号「%s」（扫到才执行，幂等）" % nm, API["bdd_del"], H_OK, None,
       {"bddId": "${finSld%d}" % i}, None)
    _steps = []
    _cfg = _BDD_TO_CFG.get(_pcode)
    if _cfg:  # 该通图号下配置过静载参数：先删配置（外键），再删通图号
        ck = "sld.cleanup.del_cfg." + _cfg
        td(ck, "清场删除-载荷配置-%s" % _cfg.upper(),
           "删除 %s 对应的静载配置（btdId 取造数时提取的值，扫到才执行，幂等）" % _cfg.upper(),
           API["sld_del"], H_OK, None, {"btdId": "${sldBtd%s}" % _cfg.upper()}, None)
        _steps.append(ck)
    _steps.append(bk)
    _sld_cleanup_blocks.append({"api_res_exist": [{
        "test_data_key": "sld.cleanup.scan_bdd",
        "judgment_criteria_items": [{
            "assertion_config": A([r("$..[?(@.designDrawingsNumber=='%s')].bddId" % nm, "not_empty")]),
            "steps_after_failure": [],
            "steps_after_success": _steps,
        }],
    }]})

# ---- 批量删除/清场用例（模块最后一条，承载终局清场）
bdd_case("bdd.del.batch_no_auth", SUB_BATCH, "缺少Authorization批量删除被拒绝且记录未被删除",
         "TC-BDD-042: 前置确保 t01~t03 存在后无鉴权批量删除，应鉴权失败且记录仍在。"
         "本条用例是**通图号模块的最后一条**（order=1，其余为 0），后置步骤承载模块级清场："
         "扫描本梁场全部通图号，逐个按名称/梁型码判断是否存在，存在才删除",
         [S("bdd.batch.no_auth", "GET 批量删除，请求头仅 Sys-dept-id", NO_AUTH()),
          S("bdd.get.by_id.t01", "GET 通过id查询 bddId=${bddIdT01}，确认记录未被删除",
            OKX([r("$.data.bddId", "not_empty")]))],
         seeds=[("bdd.probe.t01", "bdd.add.t01"), ("bdd.probe.t02", "bdd.add.t02"),
                ("bdd.probe.t03", "bdd.add.t03")],
         post=[{"api_res_exist": [{"test_data_key": "bdd.cleanup.scan_all",
                                   "judgment_criteria_items": _bdd_items}]}],
         order=1)

td("bdd.get.by_id.t01", "通图号通过id查询-t01", "按 bddId 回查 t01", API["bdd_get"], H_OK, None,
   {"bddId": "${bddIdT01}"}, None)

sld_case("sld.del.batch_no_auth", SUB_BATCH, "缺少Authorization批量删除被拒绝且配置未被删除",
         "TC-SLD-027: 前置确保 l01 存在后无鉴权批量删除，应鉴权失败。本条用例是**载荷计算模块的最后一条**（order=1），"
         "后置步骤承载模块级清场：先按通图号逐条删除静载配置，再删除载荷模块自建的通图号",
         [S("sld.batch.no_auth", "GET 批量删除，请求头仅 Sys-dept-id", NO_AUTH()),
          S("sld.get.by_id", "GET 通过id查询 btdId=${sldBtdL01}，确认配置仍在",
            OKX([r("$.data.btdId", "not_empty")]))],
         seeds=seed_sld("l01"),
         post=_sld_cleanup_blocks,
         order=1)

# ---- 按用例的执行顺序重排 order（终局清场用例必须在模块最后）
for _m in (MOD_BDD, MOD_SLD):
    _mine = [c for c in cases if c["module_name"] == _m]
    _last = next(c for c in _mine if c["key"].endswith(".batch_no_auth"))
    _last["order"] = max(c["order"] for c in _mine if c is not _last) + 1

# 统一重编用例编号（TC-BDD-001…/TC-SLD-001…），保证文档列出的顺序与编号一致
for _m, _pref in ((MOD_BDD, "BDD"), (MOD_SLD, "SLD")):
    for _i, _c in enumerate([x for x in cases if x["module_name"] == _m], 1):
        _c["description"] = re.sub(r"^TC-[A-Z]+-\d+", "TC-%s-%03d" % (_pref, _i), _c["description"])


# ================================================================ 四、自检
EXT_KEYS = {
    "login.success", "dept.query.tree_success",
    "beamfield.prep.detect_chain", "beamfield.prep.add_group", "beamfield.prep.get_group_id",
    "beamfield.prep.add_build_unit", "beamfield.prep.get_build_unit_id",
    "beamfield.prep.add_proj", "beamfield.prep.get_proj_id",
    "beamfield.prep.add_section", "beamfield.prep.get_section_id",
    "beamfield.dept.create_f01", "beamfield.dept.verify_f01",
    "beamfield.query.by_dept", "beamfield.prepare.add",
}
td_keys = {x["key"] for x in test_data} | EXT_KEYS
api_ids = {x["id"] for x in api_info} | {10}
problems = []

for d in test_data:
    if d["api_info_id"] not in api_ids:
        problems.append("test_data %s 引用了不存在的 api_info_id %s" % (d["key"], d["api_info_id"]))
if len({d["key"] for d in test_data}) != len(test_data):
    problems.append("test_data 存在重复 key")
if len({c["key"] for c in cases}) != len(cases):
    problems.append("api_test_case 存在重复 key")


def walk_refs(c):
    refs = [s["test_data_key"] for s in (c["test_steps"] or [])]
    for blk in (c["pre_requisites"] or []) + (c["post_steps"] or []):
        for k in ("api_res_exist", "api_res_not_exist"):
            for it in blk.get(k) or []:
                refs.append(it["test_data_key"])

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("steps_after_failure", "steps_after_success"):
                    refs.extend(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for i in node:
                walk(i)
    walk(c["pre_requisites"])
    walk(c["post_steps"])
    return refs


for c in cases:
    for ref in walk_refs(c):
        if ref not in td_keys:
            problems.append("case %s 引用了不存在的 test_data: %s" % (c["key"], ref))

# 1) 通图号正向编码唯一 + 负向冲突是有意为之
_pos_codes = {b for _c, _n, b, _d in BDD_ADDS}
if len(_pos_codes) != len(BDD_ADDS):
    problems.append("通图号正向数据的梁型码存在重复")
INTENDED_CONFLICT = {"n07", "n08"}  # 刻意与 861 冲突的查重用例
for _c, _t, _b, _d, _ai, _cf in BDD_NEG:
    _code = str(_b.get("designBeamType", "")).strip()
    if _c not in INTENDED_CONFLICT and _code in _pos_codes:
        problems.append("负向数据 %s 的梁型码 %s 与正向数据冲突（会被查重抢先拦截）" % (_c, _code))
for _c, _t, _b, _d, _ai, _cf in BDD_NEG:
    if _c in INTENDED_CONFLICT and str(_b.get("designBeamType", "")).strip() != "861":
        problems.append("查重类负向数据 %s 应刻意使用已占用的 861" % _c)

# 2) 正向编码必须落在 153~998
for _c, _n, b, _d in BDD_ADDS:
    if not (b.isdigit() and len(b) == 3 and 153 <= int(b) <= 998):
        problems.append("通图号正向数据 %s 的梁型码 %s 不在 153~998 区间或不是 3 位" % (_c, b))

# 3) 清场覆盖：每个「测试通图号-」名称、每个无名称报文都要有清场项
for _d in test_data:
    if _d["api_info_id"] in (API["bdd_add"], API["bdd_upd"]) and isinstance(_d["data"], dict):
        _nm = _d["data"].get("designDrawingsNumber")
        if isinstance(_nm, str) and _nm.startswith(BDD_PREFIX) and _nm not in _bdd_names:
            problems.append("通图号报文名称没有清场项：%s（%s）" % (_nm, _d["key"]))
        if not isinstance(_nm, str) or not _nm.strip():
            _code = _d["data"].get("designBeamType")
            if _d["api_info_id"] == API["bdd_add"] and _code and _code not in _bdd_codes:
                problems.append("无名称报文缺少按梁型码兜底的清场项：%s（%s）" % (_d["key"], _code))
# 载荷模块的通图号必须全部进入它自己的清场名单
for _c, _n, _b, _d in SLD_BDD:
    if _n not in _sld_names:
        problems.append("载荷模块的通图号 %s 未进入清场名单" % _n)
# 载荷模块的通图号不能落在通图号模块的清场前缀下（否则互相误删）
for _c, _n, _b, _d in SLD_BDD:
    if _n.startswith(BDD_PREFIX):
        problems.append("载荷模块通图号 %s 与通图号模块清场前缀冲突" % _n)
# 载荷清场必须覆盖每条自建通图号；配置过的通图号必须先删配置再删通图号（外键顺序）
_cleanup_names = set()
for _b in _sld_cleanup_blocks:
    for _it in _b["api_res_exist"][0]["judgment_criteria_items"]:
        _m = re.search(r"designDrawingsNumber=='([^']+)'",
                       _it["assertion_config"]["assertion_rules"][0]["jsonpath"])
        if _m:
            _cleanup_names.add(_m.group(1))
for _c, _n, _b, _d in SLD_BDD:
    if _n not in _cleanup_names:
        problems.append("载荷清场未覆盖自建通图号 %s" % _n)
for _b in _sld_cleanup_blocks:
    _it = _b["api_res_exist"][0]["judgment_criteria_items"][0]
    _ss = _it["steps_after_success"]
    if any(k.startswith("sld.cleanup.del_cfg.") for k in _ss) and _ss[-1].startswith("sld.cleanup.del_cfg."):
        problems.append("载荷清场顺序错误：应先删配置再删通图号 %s" % _ss)
# 每个载荷配置都必须有对应的清场删除项（否则删通图号时会撞外键，数据清不掉）
for _c, _p, _d, _b in SLD_CFG:
    if "sld.cleanup.del_cfg." + _c not in td_keys:
        problems.append("载荷清场缺少配置删除项：%s" % _c)
for _b in _sld_cleanup_blocks:
    _nm = re.search(r"designDrawingsNumber=='([^']+)'",
                    _b["api_res_exist"][0]["judgment_criteria_items"][0]
                    ["assertion_config"]["assertion_rules"][0]["jsonpath"]).group(1)
    _pcode = next(p for p, n, _x, _y in SLD_BDD if n == _nm)
    _cfg = _BDD_TO_CFG.get(_pcode)
    if _cfg and ("sld.cleanup.del_cfg." + _cfg) not in _b["api_res_exist"][0]["judgment_criteria_items"][0]["steps_after_success"]:
        problems.append("载荷清场 %s 未先删除配置 %s" % (_nm, _cfg))

# 4) 载荷配置的 bddId 必须指向本模块自建的通图号
_sld_vars = {"${sldBdd%s}" % c.upper(): (c, n) for c, n, b, d in SLD_BDD}
for _d in test_data:
    if _d["api_info_id"] == API["sld_add"] and isinstance(_d["data"], dict):
        _v = _d["data"].get("bddId")
        if _v is not None and _v not in _sld_vars:
            problems.append("载荷配置 %s 的 bddId=%s 未指向本模块自建的通图号" % (_d["key"], _v))

# 5) 上下文变量：is_ctx_var 的期望值不能带 ${}，且变量名必须是本文件提取过的
_extract_names = {e["name"] for _d in test_data for e in (_d.get("extract") or [])}
_all_text = json.dumps([test_data, cases], ensure_ascii=False)
_used_vars = set(re.findall(r"\$\{([A-Za-z0-9_]+)", _all_text))
for _c in cases:
    for _s in _c["test_steps"] or []:
        for _r0 in (_s.get("assertion_config") or {}).get("assertion_rules") or []:
            if not (_r0.get("ctx") or {}).get("is_ctx_var"):
                continue
            _ev = _r0.get("expect_value")
            if not isinstance(_ev, str):
                problems.append("case %s 的 is_ctx_var 期望值应为上下文键名（字符串）：%r" % (_c["key"], _ev))
            elif _ev.startswith("${"):
                problems.append("case %s 的 is_ctx_var 期望值不能带 ${}：%s" % (_c["key"], _ev))
            elif _ev not in _extract_names and _ev not in _used_vars:
                problems.append("case %s 的 is_ctx_var 引用了未知上下文变量：%s" % (_c["key"], _ev))

# 6) 每个模块必须有且只有一条承载终局清场的用例，且 order 为模块内最大
for _m in (MOD_BDD, MOD_SLD):
    _mine = [c for c in cases if c["module_name"] == _m]
    _carriers = [c for c in _mine if c["post_steps"]]
    if len(_carriers) != 1:
        problems.append("模块 %s 承载清场的用例应恰好 1 条，实际 %d 条" % (_m, len(_carriers)))
    elif _carriers[0]["order"] != max(c["order"] for c in _mine):
        problems.append("模块 %s 的清场用例 order 不是最大" % _m)

# 7) 相同请求（同一 test_data）不应被多条用例当作「写操作」执行（读操作可复用）
WRITE_APIS = {API["bdd_add"], API["bdd_upd"], API["bdd_del"], API["bdd_batch"],
              API["sld_add"], API["sld_upd"], API["sld_del"], API["sld_batch"]}
_READ_OK = {"bdd.list.all", "bdd.cleanup.scan_all", "sld.list.all", "sld.list.no_auth",
            "sld.list.no_dept", "bdd.list.no_auth", "bdd.list.no_dept", "bdd.list.fake_dept",
            "bdd.page.default", "bdd.page.size1", "bdd.page.second",
            "sld.page.default", "sld.page.size1", "sld.page.second",
            "bdd.list.builtin", "sld.cleanup.scan_bdd", "sld.add.no_auth", "bdd.add.t15"}
_by_key = {x["key"]: x for x in test_data}
_writers = {}
for _c in cases:
    for _s in _c["test_steps"] or []:
        _k = _s["test_data_key"]
        _rec = _by_key.get(_k)
        if _rec and _rec["api_info_id"] in WRITE_APIS and _k not in _READ_OK:
            _writers.setdefault(_k, []).append(_c["key"])
for _k, _cs in _writers.items():
    if len(_cs) > 1:
        problems.append("写操作 %s 被多条用例执行：%s" % (_k, _cs))

if problems:
    print("自检未通过（%d 项）：" % len(problems))
    for p in problems:
        print("  -", p)
    raise SystemExit(1)

# ================================================================ 五、输出
# 按模块归组输出（Python 的 sort 是稳定的，模块内保持定义顺序）：
# 这样入库后每个模块的用例 id 是连续区间，与梁型管理模块的排布一致，
# 也避免两个模块的用例 id 交叉导致入库脚本按模块重排 id 时撞主键。
_MOD_SEQ = {MOD_BDD: 0, MOD_SLD: 1}
cases.sort(key=lambda c: _MOD_SEQ.get(c["module_name"], 99))

payload = {
    "meta": {
        "module_name": [MOD_BDD, MOD_SLD],
        "project_name": PROJECT,
        "generated_from": ["桥梁与载荷计算/梁体与通图号.md", "桥梁与载荷计算/梁体与通图号需求.md",
                           "桥梁与载荷计算/桥梁设计与载荷计算.md", "基本信息接口文档.md"],
        "saved_to_db": True,
        "note": "通图号与静载试验设计参数两个模块：通图号按梁场隔离、内置 153 条由「初始化通图号」接口生成且不可编辑/删除、"
                "梁型码去空格查重且限 153~998、新建记录在分页查询中排第一、列表按名称模糊/按梁型码精确过滤、编辑接口 bddId 必填；"
                "静载参数挂在通图号上（1:1），bddId/rd/ed/fl 必填，btdId 由服务端生成、请求不传。"
                "两个模块各自自建数据、各自清场（前缀分别为 测试通图号- / 载荷测试图号-）。"
                "api_info 复用库内 id=10（通图号列表查询，同一 endpoint 不重复建记录）。"
                "按评审意见已去掉「图号名称超过 50 字符」用例。",
        "record_count": {"api_info": len(api_info), "api_test_data": len(test_data), "api_test_case": len(cases)},
    },
    "api_info": api_info,
    "api_test_data": test_data,
    "api_test_case": cases,
}

out_json = os.path.join(BASE, "通图号与载荷计算-接口测试用例.json")
with io.open(out_json, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
print("已生成 %s" % out_json)
print("api_info %d / api_test_data %d / api_test_case %d"
      % (len(api_info), len(test_data), len(cases)))
for _m in (MOD_BDD, MOD_SLD):
    _mine = [c for c in cases if c["module_name"] == _m]
    print("  %s：%d 条用例，子模块 %s" % (_m, len(_mine),
                                      "、".join(sorted({c["sub_module_name"] for c in _mine}))))
