# -*- coding: utf-8 -*-
"""
梁型管理（梁体类型 + 通图号取值）接口测试用例生成器
产出：梁型管理-接口测试用例.json（不写入数据库）
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "组织机构管理系统"
MODULE = "梁型管理"

H_OK = {"Authorization": "${loginUserToken}", "Sys-dept-id": "${bfDeptId}"}
H_NO_AUTH = {"Sys-dept-id": "${bfDeptId}"}
H_NO_DEPT = {"Authorization": "${loginUserToken}"}
H_FAKE_DEPT = {"Authorization": "${loginUserToken}", "Sys-dept-id": "999999999"}

API = {
    "sjth": 10,   # 通图号列表
    "page": 11,   # 梁型分页查询
    "list": 12,   # 梁型列表查询
    "add": 13,    # 梁型新增
    "update": 14, # 梁型编辑
    "get": 15,    # 梁型通过id查询
    "del": 16,    # 梁型通过id删除
    "batch": 17,  # 梁型批量删除
}

api_info = [
    {"id": 10, "name": "梁体通图号列表查询", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "通图号", "endpoint": "/api/base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoList.ajax",
     "method": "GET", "response_model": "DesignDrawNumberRes", "swagger_md_text": None,
     "description": "查询通图号列表，返回 bddId（即梁型的 sjth，系统自动生成，不需要新增），梁型新增/编辑时直接取用"},
    {"id": 11, "name": "梁型分页列表查询", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "分页列表查询", "endpoint": "/api/base/bfmBeamType/queryBfmBeamTypeVoPage.ajax",
     "method": "GET", "response_model": "BeamTypePageResponse", "swagger_md_text": None,
     "description": "分页查询当前梁场的梁型列表，query 参数为 pageNum、pageSize，返回 data.total 与 data.list"},
    {"id": 12, "name": "梁型列表查询", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "列表查询", "endpoint": "/api/base/bfmBeamType/queryBfmBeamTypeVoList.ajax",
     "method": "GET", "response_model": "BeamTypeListResponse", "swagger_md_text": None,
     "description": "按 name/beamBodyType/beamLengthType/sjth/barrierType/lineType/zpType/beamLocation 过滤查询梁型列表，全部为可选参数，返回 data 数组"},
    {"id": 13, "name": "梁型新增", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "新增", "endpoint": "/api/base/bfmBeamType/addBfmBeamType.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "新增梁型，必填 name/beamBodyType/beamLengthType/beamLength/sjth/barrierType/lineType/zpType/planTotal/beamTypeColor（共 10 项）；beamLocation 为条件必填：T 梁（beamBodyType=1）必填，箱梁（beamBodyType=2）可不传；成功不返回主键，btId 需再查列表获取"},
    {"id": 14, "name": "梁型编辑", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "编辑", "endpoint": "/api/base/bfmBeamType/updateBfmBeamType.ajax",
     "method": "POST", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "编辑梁型，btId 必填（写在请求体中，标识要改的记录），其余字段语义同新增（必填项需全量回传）"},
    {"id": 15, "name": "梁型通过id查询", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "通过id查询", "endpoint": "/api/base/bfmBeamType/queryBfmBeamTypeById.ajax",
     "method": "GET", "response_model": "BeamTypeDetailResponse", "swagger_md_text": None,
     "description": "按主键 btId 查询单个梁型，data 为对象"},
    {"id": 16, "name": "梁型通过id删除", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "通过id删除", "endpoint": "/api/base/bfmBeamType/deleteBfmBeamType.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按主键 btId 删除单个梁型，参数 btId 必填"},
    {"id": 17, "name": "梁型批量删除", "project_name": PROJECT, "module_name": MODULE,
     "sub_module_name": "批量删除", "endpoint": "/api/base/bfmBeamType/deleteBfmBeamTypeBatch.ajax",
     "method": "GET", "response_model": "BaseCsrdResponseModel", "swagger_md_text": None,
     "description": "按 btIds（多个主键用英文逗号拼接）批量删除梁型"},
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
    return {"name": name, "jsonpath": jsonpath, "handle": {"handle_method": "get_index", "handle_param": {"index": index}},
            "description": description}


def body(name, body_type="2", len_type="1", length=32.6, sjth="${sjthA}", barrier="1",
         line="2", zp="1", beam_location=None, plan=120, color="#1F6FD0", with_color=True):
    b = {"name": name, "beamBodyType": body_type, "beamLengthType": len_type, "beamLength": length,
         "sjth": sjth, "barrierType": barrier, "lineType": line, "zpType": zp}
    if beam_location is not None:
        b["beamLocation"] = beam_location
    b["planTotal"] = plan
    if with_color:
        b["beamTypeColor"] = color
    return b


def r(path, op, val=None):
    return {"jsonpath": path, "operator": op, "expect_value": val}


def rv(path, op, var):
    """expect_value 取系统上下文变量：填键名（不带 ${}），并用 ctx.is_ctx_var=True 标记

    执行器（assertion_engine.run_one）在派发操作符前会把它替换成上下文里的实际值，
    所以任何操作符（eq / contains / gt ...）都能直接用上下文变量做期望值。
    """
    return {"jsonpath": path, "operator": op, "expect_value": var, "ctx": {"is_ctx_var": True}}


def A(rules, ai=None):
    return {"assertion_rules": rules, "ai_assertion_rule": ai}


OK = A([r("$", "res_contains_data", {"status": "1", "code": "200"})])


def OKX(extra, ai=None):
    return A([r("$", "res_contains_data", {"status": "1", "code": "200"})] + extra, ai)


def FAIL(ai="message 应为明确的业务提示（必填项缺失 / 参数非法 / 名称重复 / 数据不存在等），不得返回内部异常或 500"):
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


def PRE(with_sjth=True, min_sjth=9):
    """公共前置：令牌 → 组织机构链路（梁场 F01 / bfDeptId）→ 通图号可用

    min_sjth：要求通图号至少有多少条（判据为 length_gt min_sjth）。
    基础数据用例要取第 11 条（sjthK），因此传 min_sjth=10。
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
    ]
    # 梁场基本信息 bfmBeamField：本梁场没有记录时才新增（初始化数据，模块清场不删除）
    p.append({"api_res_not_exist": [{
        "test_data_key": "beamfield.query.by_dept",
        "judgment_criteria_items": [{
            "assertion_config": A([r("$.data", "length_gt", 0)]),
            "steps_after_failure": [],
            "steps_after_success": ["beamfield.prepare.add"],
        }],
    }]})
    if with_sjth:
        # 系统自带 10 条以上通图号，本模块按用途分组取用 sjthA~sjthK（共 11 条），因此这里要求至少 min_sjth+1 条；
        # 数量不足时前置直接失败并提示，避免提取到空值后在用例里报出难以定位的错误。
        p.append({"api_res_exist": [{
            "test_data_key": "beamtype.sjth.list",
            "judgment_criteria_items": [{
                "assertion_config": A([r("$.data", "length_gt", min_sjth)]),
                "steps_after_success": [],
                "steps_after_failure": [],
            }],
        }]})
    return p


def seed_block(probe_key, add_key, recheck=False):
    """前置「先查后建」：探针查不到（数据不存在）才新增；查到（已存在）就跳过新增。

    判据写的是「怎样算存在」（data 长度 > 0），由执行器按 api_res_not_exist 反转：
    判据不成立 → 不存在成立 → 走 steps_after_success；判据成立 → 已存在 → 走 steps_after_failure。
    recheck=True 时新增后再查一次探针，用于提取 btId（新增接口不返回主键）。
    """
    return {"api_res_not_exist": [{
        "test_data_key": probe_key,
        "judgment_criteria_items": [{
            "assertion_config": A([r("$.data", "length_gt", 0)]),
            "steps_after_success": [add_key] + ([probe_key] if recheck else []),
            "steps_after_failure": [],
        }],
    }]}


def case(key, sub, title, desc, steps, pre=None, post=None, active=1, order=0, seeds=None):
    p = PRE() if pre is None else pre
    for _s in seeds or []:
        p.append(seed_block(*_s))
    cases.append({
        "key": key, "module_name": MODULE, "sub_module_name": sub,
        "title": title, "description": desc,
        "pre_requisites": p,
        "post_steps": post, "test_steps": steps, "is_active": active,
        "order": order,
    })


# 梁型列表返回的 12 个字段
BT_KEYS = ["btId", "name", "beamBodyType", "beamLengthType", "beamLength", "sjth",
           "barrierType", "lineType", "zpType", "beamLocation", "planTotal", "beamTypeColor"]


# ---------------------------------------------------------------- 1. 数据准备
td("beamtype.sjth.list", "通图号列表查询-提取可用sjth",
   "查询通图号管理已初始化的通图号，提取 bddId 作为梁型的 sjth（系统自动生成，不新增，直接取用）",
   API["sjth"], H_OK, None, None,
   [ex("sjthA", "$.data[0].bddId", "第 1 条通图号：基础新增组（A01~A05、判重/颜色/同名基线、SQL 注入数据）"),
    ex("sjthB", "$.data[1].bddId", "第 2 条通图号：「编辑-更换通图号」用例的目标值（U02 由 sjthG 改为 sjthB）"),
    ex("sjthC", "$.data[2].bddId", "第 3 条通图号：Q03 独占，专供「按通图号查询」做精确断言（该通图号下只有 1 条记录）"),
    ex("sjthD", "$.data[3].bddId", "第 4 条通图号：列表查询组（Q01/Q02/Q05）"),
    ex("sjthE", "$.data[4].bddId", "第 5 条通图号：分页查询组（P01/P02A/P02B/P03）"),
    ex("sjthF", "$.data[5].bddId", "第 6 条通图号：通过id查询组（G01）"),
    ex("sjthG", "$.data[6].bddId", "第 7 条通图号：编辑组（U01~U07，U02 编辑时改为 sjthB）"),
    ex("sjthH", "$.data[7].bddId", "第 8 条通图号：通过id删除组（D01~D03）"),
    ex("sjthI", "$.data[8].bddId", "第 9 条通图号：批量删除组（B01~B05）"),
    ex("sjthJ", "$.data[9].bddId", "第 10 条通图号：模糊匹配组（F01/F02）"),
    ex("sjthK", "$.data[10].bddId", "第 11 条通图号：基础数据专用（`基础梁型-*` 共 16 条，与用例造数隔离，执行完不清理）"),
    ex("sjthDrawingA", "$.data[0].designDrawingsNumber", "第 1 条通图号的图号，用于核对 sjth 对应的业务含义"),
    ex("sjthBeamCodeA", "$.data[0].designBeamType", "第 1 条通图号的梁型码")])

# 新增用例的造数
# 通图号（sjth）按用途分组取用系统自带的 10 条：A=基础新增组、B=编辑更换的目标值、C=Q03 独占（供按通图号精确查询）、
# D=列表查询组、E=分页组、F=通过id查询、G=编辑组、H=通过id删除组、I=批量删除组、J=模糊匹配组。
# 一条通图号下挂一组梁型，比全部挤在同一条上更接近真实数据，也让「按通图号过滤」能拿到确定性结果。
# 系统判重规则：梁体类型 + 长度类型 + 通图号 + 正线类型 + 声屏障 + T梁位置 + 直曲类别
# 这 7 项完全相同即判定为重复；架设图例颜色 beamTypeColor 在**全梁场范围内唯一**（跨梁体类型也不能重复）；
# 梁型名称不做唯一校验。因此下面每条造数的「7 项组合」与「图例颜色」都必须互不相同（文件末尾有自检，冲突直接报错）。
# 字段顺序：code, 名称, 说明, 梁体类型, 长度类型, 跨度, 通图号, 声屏障, 正线类型, 直曲类别, T梁位置, 计划数量, 图例颜色
ADDS = [
    ("a01", "测试梁型-32m双线箱梁-A01", "箱梁 / 32 米 / 双线 / 有声屏障 / 直线，计划 120 榀",
     "2", "1", 32.6, "${sjthA}", "1", "2", "1", None, 120, "#1F6FD0"),
    ("a02", "测试梁型-24m单线T梁-A02", "T 梁 / 24 米 / 单线 / 无声屏障 / 曲线 / 中梁，计划 64 榀",
     "1", "2", 24.6, "${sjthA}", "0", "1", "2", "1", 64, "#C00000"),
    ("a03", "测试梁型-20m仅必填-A03", "只传 10 个必填字段（含架设图例颜色）；箱梁不传条件必填的 beamLocation",
     "2", "3", 20.6, "${sjthA}", "0", "1", "1", None, 40, "#4C1D95"),
    ("a04", "测试梁型-40m其他-A04", "长度类型 6（其他）/ 跨度 40.375（三位小数）/ 计划 1（最小值）",
     "2", "6", 40.375, "${sjthA}", "1", "2", "2", None, 1, "#00843D"),
    ("a05.seed", "测试梁型-判重基线-A05", "T 梁 / 24 米 / 单线 / 无声 / 中梁 / 直线，作为「组合重复」用例的基线（颜色 #7030A0）",
     "1", "2", 24.6, "${sjthA}", "0", "1", "1", "1", 32, "#7030A0"),
    ("q01", "测试梁型-32m双线箱梁-Q01", "箱梁 / 32 米 / 双线 / 有声 / 曲线，用于「列表查询-无参」",
     "2", "1", 32.6, "${sjthD}", "1", "2", "2", None, 100, "#2E8B57"),
    ("q02", "测试梁型-24m单线T梁-Q02", "T 梁 / 24 米 / 单线 / 有声 / 边梁 / 曲线，用于「列表查询-按名称」（与 A02 至少差两项，避免只差 T 梁位置一项）",
     "1", "2", 24.6, "${sjthD}", "1", "1", "2", "2", 60, "#8B4513"),
    ("q03", "测试梁型-24m单线箱梁-Q03", "箱梁 / 24 米 / 单线 / 有声 / 直线，用于「列表查询-按通图号」",
     "2", "2", 24.6, "${sjthC}", "1", "1", "1", None, 45, "#2F4F4F"),
    ("q05", "测试梁型-24m单线箱梁-Q05", "箱梁 / 24 米 / 单线 / 无声 / 直线，用于「列表查询-按梁体类型」",
     "2", "2", 24.6, "${sjthD}", "0", "1", "1", None, 55, "#A0522D"),
    ("p01", "测试梁型-32m双线箱梁-P01", "箱梁 / 32 米 / 双线 / 无声 / 直线，用于「分页查询-第1页」",
     "2", "1", 32.6, "${sjthE}", "0", "2", "1", None, 100, "#3CB371"),
    ("p02a", "测试梁型-24m双线箱梁-P02A", "箱梁 / 24 米 / 双线 / 有声 / 直线（第 1 页数据）",
     "2", "2", 24.6, "${sjthE}", "1", "2", "1", None, 80, "#20B2AA"),
    ("p02b", "测试梁型-20m双线箱梁-P02B", "箱梁 / 20 米 / 双线 / 无声 / 直线（第 2 页数据）",
     "2", "3", 20.6, "${sjthE}", "0", "2", "1", None, 70, "#B8860B"),
    # 每页 1 条的分页用例必须独立造数：P02A 已由「第 2 页」用例创建，若两个用例共用同一条新增数据，
    # 第二次执行会因七项要素 + 颜色完全相同被判重，新增直接返回「梁型重复」
    ("p03", "测试梁型-40m单线箱梁-P03", "箱梁 / 40.375 米 / 单线 / 有声 / 曲线，用于「分页查询-每页1条」",
     "2", "6", 40.375, "${sjthE}", "1", "1", "2", None, 50, "#00CED1"),
    ("g01", "测试梁型-32m双线箱梁-G01", "箱梁 / 32 米 / 双线 / 无声 / 曲线，字段值与「通过id查询」断言一一对应",
     "2", "1", 32.6, "${sjthF}", "0", "2", "2", None, 100, "#4682B4"),
    ("u01", "测试梁型-32m单线箱梁-U01", "箱梁 / 32 米 / 单线 / 有声 / 直线，用于「编辑-全字段修改」",
     "2", "1", 32.6, "${sjthG}", "1", "1", "1", None, 100, "#5F9EA0"),
    ("u02", "测试梁型-24m单线T梁-U02", "T 梁 / 24 米 / 单线 / 有声 / 次边梁 / 曲线，用于「编辑-更换通图号」",
     "1", "2", 24.6, "${sjthG}", "1", "1", "2", "3", 64, "#DC143C"),
    ("u03", "测试梁型-20m双线T梁-U03", "T 梁 / 20 米 / 双线 / 无声 / 中梁 / 直线，用于「编辑-T梁位置」",
     "1", "3", 20.6, "${sjthG}", "0", "2", "1", "1", 64, "#E9967A"),
    ("u04", "测试梁型-32m单线箱梁-U04", "箱梁 / 32 米 / 单线 / 有声 / 曲线，用于「编辑-缺少name」",
     "2", "1", 32.6, "${sjthG}", "1", "1", "2", None, 100, "#6A5ACD"),
    ("u06", "测试梁型-32m单线箱梁-U06", "箱梁 / 32 米 / 单线 / 无声 / 直线，用于「编辑-缺少Sys-dept-id」",
     "2", "1", 32.6, "${sjthG}", "0", "1", "1", None, 100, "#778899"),
    ("u07", "测试梁型-24m双线箱梁-U07", "箱梁 / 24 米 / 双线 / 无声 / 曲线，用于「编辑-缺少Authorization」",
     "2", "2", 24.6, "${sjthG}", "0", "2", "2", None, 100, "#8FBC8F"),
    ("d01", "测试梁型-20m双线箱梁-D01", "箱梁 / 20 米 / 双线 / 有声 / 曲线，用于「通过id删除-成功」",
     "2", "3", 20.6, "${sjthH}", "1", "2", "2", None, 100, "#4169E1"),
    ("d02", "测试梁型-24m单线T梁-D02", "T 梁 / 24 米 / 单线 / 无声 / 次边梁 / 直线，用于「通过id删除-缺少Authorization」",
     "1", "2", 24.6, "${sjthH}", "0", "1", "1", "3", 64, "#FF8C00"),
    ("d03", "测试梁型-20m单线箱梁-D03", "箱梁 / 20 米 / 单线 / 有声 / 直线，用于「通过id删除-重复删除」",
     "2", "3", 20.6, "${sjthH}", "1", "1", "1", None, 70, "#B22222"),
    ("b01", "测试梁型-24m单线箱梁-B01", "箱梁 / 24 米 / 单线 / 有声 / 曲线（第 1 条待批量删除）",
     "2", "2", 24.6, "${sjthI}", "1", "1", "2", None, 100, "#6B8E23"),
    ("b02", "测试梁型-24m双线T梁-B02", "T 梁 / 24 米 / 双线 / 无声 / 中梁 / 曲线（第 2 条待批量删除）",
     "1", "2", 24.6, "${sjthI}", "0", "2", "2", "1", 64, "#DB7093"),
    ("b03", "测试梁型-20m双线箱梁-B03", "箱梁 / 20 米 / 双线 / 有声 / 直线（含无效ID的批量删除）",
     "2", "3", 20.6, "${sjthI}", "1", "2", "1", None, 70, "#8B008B"),
    ("b04", "测试梁型-24m单线箱梁-B04", "箱梁 / 24 米 / 单线 / 无声 / 曲线（无鉴权批量删除-第 1 条）",
     "2", "2", 24.6, "${sjthI}", "0", "1", "2", None, 100, "#7B68EE"),
    ("b05", "测试梁型-24m双线T梁-B05", "T 梁 / 24 米 / 双线 / 有声 / 中梁 / 直线（无鉴权批量删除-第 2 条）",
     "1", "2", 24.6, "${sjthI}", "1", "2", "1", "1", 64, "#BDB76B"),
    ("f01", "测试梁型-模糊匹配-箱梁-F01", "箱梁 / 24 米 / 双线 / 有声 / 曲线，名称含公共前缀「测试梁型-模糊匹配」",
     "2", "2", 24.6, "${sjthJ}", "1", "2", "2", None, 110, "#D2691E"),
    ("f02", "测试梁型-模糊匹配-T梁-F02", "T 梁 / 24 米 / 双线 / 有声 / 边梁 / 曲线，名称含公共前缀「测试梁型-模糊匹配」",
     "1", "2", 24.6, "${sjthJ}", "1", "2", "2", "2", 60, "#FF6347"),
]

# ---------------------------------------------------------------- 1.1 基础数据（正交组合，不是测试用例造数）
# 用途：给手工测试 / 其它测试直接使用的梁型基础数据，与测试用例的造数**完全隔离**：
#   · 名称前缀 `基础梁型-`——模块清场只删 `测试梁型-`，这批数据执行完会长期保留；
#   · 通图号独占第 11 条（`${sjthK}`），与用例造数使用的 sjthA~sjthJ 不重叠，
#     七项判重组合因此天然不会与用例造数撞车；
#   · 图例颜色取尚未使用过的色值（颜色全梁场唯一，自检会复核）。
# 组合方式：梁体类型(2) × 跨度(4) × 声屏障(2) 取**全因子正交**（共 16 条），
# 正线类型 / 直曲类别 / T梁位置 / 计划数量 按配平后的表分配，
# 任意两个因子的水平组合都至少出现一次（文件末尾有覆盖率自检，缺组合直接报错）。
BASE_PREFIX = "基础梁型-"
BASE_BODY = [("1", "T梁"), ("2", "箱梁")]
BASE_SPAN = [("3", 20.6, "20m"), ("2", 24.6, "24m"), ("1", 32.6, "32m"), ("6", 40.375, "40.375m")]
BASE_BARRIER = [("0", "无声"), ("1", "有声")]
BASE_PLAN = [24, 48, 96]
BASE_LOC = {"1": "中梁", "2": "边梁", "3": "次边梁"}
# 与已用的 46 个色值均不重复
BASE_COLORS = ["#2C3E50", "#34495E", "#16A085", "#27AE60", "#2980B9", "#8E44AD",
               "#9B59B6", "#D35400", "#E74C3C", "#7F8C8D", "#1ABC9C", "#B03A2E",
               "#1F3A93", "#4A235A", "#0E6251", "#6E2C00"]

BASE_ROWS = []
for _s_i, (_lt, _ln, _lbl) in enumerate(BASE_SPAN):
    for _b_i, (_bt, _btl) in enumerate(BASE_BODY):
        for _r_i, (_bar, _barl) in enumerate(BASE_BARRIER):
            _line = "1" if (_s_i + _b_i) % 2 == 0 else "2"
            _zp = "1" if (_s_i + _b_i + _r_i) % 2 == 0 else "2"
            _loc = None if _bt == "2" else str((_s_i + _r_i) % 3 + 1)
            _idx = len(BASE_ROWS)
            _code = "b%02d" % (_idx + 1)
            BASE_ROWS.append({
                "code": _code,
                "name": "基础梁型-%s-%s-%s-%s-%s%s-%s" % (
                    _btl, _lbl, "单线" if _line == "1" else "双线", _barl,
                    "直线" if _zp == "1" else "曲线",
                    ("-" + BASE_LOC[_loc]) if _loc else "", _code.upper()),
                "body": _bt, "body_label": _btl, "len_type": _lt, "length": _ln, "span_label": _lbl,
                "barrier": _bar, "barrier_label": _barl,
                "line": _line, "line_label": "单线" if _line == "1" else "双线",
                "zp": _zp, "zp_label": "直线" if _zp == "1" else "曲线",
                "loc": _loc, "loc_label": BASE_LOC[_loc] if _loc else "不适用（箱梁）",
                "plan": BASE_PLAN[_idx % 3], "color": BASE_COLORS[_idx],
            })

for _row in BASE_ROWS:
    td("beamtype.base.add." + _row["code"], "基础数据-" + _row["name"],
       "%s / 跨度 %sm（长度类型 %s）/ %s / %s屏障 / %s / T型梁位置：%s；计划数量 %d 榀；通图号取第 11 条 ${sjthK}。"
       "供手工测试直接使用，不属于测试用例造数（模块清场不删除）"
       % (_row["body_label"], _row["span_label"], _row["len_type"], _row["line_label"],
          _row["barrier_label"], _row["zp_label"], _row["loc_label"], _row["plan"]),
       API["add"], H_OK,
       body(_row["name"], _row["body"], _row["len_type"], _row["length"], "${sjthK}",
            _row["barrier"], _row["line"], _row["zp"], _row["loc"], _row["plan"], _row["color"]),
       None, None)
    td("beamtype.base.probe." + _row["code"], "存在性探针-" + _row["name"],
       "按 名称+梁体类型+长度类型 查询该条基础数据是否已存在；前置据此判断「没有才新增」，重复执行不会撞判重",
       API["list"], H_OK, None,
       {"name": _row["name"], "beamBodyType": _row["body"], "beamLengthType": _row["len_type"]}, None)

td("beamtype.base.verify", "基础数据-汇总校验（按名称前缀查询）",
   "按名称前缀「基础梁型-」模糊查询，逐个确认 %d 条基础数据都已存在" % len(BASE_ROWS),
   API["list"], H_OK, None, {"name": BASE_PREFIX}, None)

# 需要「新增后按名称回查并提取 btId」的数据（后续用例会引用这些变量）
VERIFY_CODES = ["a01", "a02", "a03", "a04", "g01",
                "u01", "u02", "u03", "u04", "u06", "u07",
                "d01", "d02", "d03", "b01", "b02", "b03", "b04", "b05"]


def add_var(code):
    return "btId" + code.replace(".", "").upper()


for _code, _name, _desc, _bt, _lt, _ln, _sjth, _bar, _line, _zp, _loc, _plan, _color in ADDS:
    td("beamtype.add." + _code, "新增-" + _name, _desc, API["add"], H_OK,
       body(_name, _bt, _lt, _ln, _sjth, _bar, _line, _zp, _loc, _plan,
            _color or "#000000", with_color=_color is not None), None, None)
    if _code in VERIFY_CODES:
        # 这条「按名称回查」既用于新增后提取 btId，也复用为删除/批量删除后的存在性校验（同一请求不重复建数据）
        td("beamtype.by_name." + _code, "按名称回查 %s 并提取btId" % _name,
           "按名称精确查询该记录并提取 btId；同一请求同时被删除类用例复用为存在性校验",
           API["list"], H_OK, None, {"name": _name},
           [ex(add_var(_code), "$..[?(@.name=='%s')].btId" % _name, "%s 的 btId" % _name)])

# ---- 「先查后建」探针：前置据此判断该条造数是否已存在（存在就不新增，避免判重导致前置失败）
# 按 名称 + 梁体类型 + 长度类型 定位（比只按名称精确：同名测试数据 A17 的两条同名、长度类型不同）。
# 这些造数没有 by_name 回查（不需要 btId），所以单独建探针；需要 btId 的直接复用 beamtype.by_name.<code>。
PROBE_META = {c[0]: (c[1], c[3], c[4]) for c in ADDS}
PROBE_META.update({
    "a16.seed": ("测试梁型-判重基线-A16", "2", "2"),
    "a17.seed": ("测试梁型-同名测试-A17", "1", "3"),
})
PROBE_CODES = ["q01", "q02", "q03", "q05", "f01", "f02",
               "p01", "p02a", "p02b", "p03", "a05.seed", "a16.seed", "a17.seed"]
for _code in PROBE_CODES:
    _name, _bt, _lt = PROBE_META[_code]
    td("beamtype.probe." + _code, "存在性探针-" + _name,
       "按 名称+梁体类型+长度类型 查询该造数是否已存在；前置据此判断「没有才新增」",
       API["list"], H_OK, None,
       {"name": _name, "beamBodyType": _bt, "beamLengthType": _lt}, None)

# 判重负向 / 名称正向用例的造数（每条用例自带基线，互不依赖，避免模块内重复新增同一条基线）
# —— 组合重复：A05 与 A14 七项要素全同，仅名称与颜色不同
td("beamtype.add.a05.dup", "新增-七项要素与A05完全相同",
   "名称（A14）与图例颜色（#4B0082）都与 A05 不同，但梁体类型/长度类型/通图号/正线类型/声屏障/T梁位置/直曲类别七项全同，应触发重复校验",
   API["add"], H_OK,
   body("测试梁型-组合重复-A14", "1", "2", 24.6, "${sjthA}", "0", "1", "1", "1", 50, "#4B0082"), None, None)
td("beamtype.add.a05.dup.verify", "回查A14未被创建", "按名称查询，确认被判重拒绝的记录没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-组合重复-A14"}, None)

# —— 颜色重复（全梁场唯一）：A16 为基线（箱梁），A15 为 T 梁，仅图例颜色相同
# 刻意让两条的梁体类型不同：若校验是「同一梁体类型内唯一」，A15 会被放行；系统为全梁场唯一，应拒绝。
td("beamtype.add.a16.seed", "新增-颜色重复用例基线A16",
   "箱梁 / 24 米 / 双线 / 无声 / 直线，图例颜色 #8B0000，作为「颜色重复」用例的基线（与 A15 梁体类型不同）",
   API["add"], H_OK,
   body("测试梁型-判重基线-A16", "2", "2", 24.6, "${sjthA}", "0", "2", "1", None, 80, "#8B0000"), None, None)
td("beamtype.add.a15.dup_color", "新增-架设图例颜色与A16相同",
   "T 梁 / 32 米 / 单线 / 无屏障 / 中梁 / 直线，图例颜色与 A16 相同（#8B0000）但梁体类型不同、七项要素也全不同；"
   "架设图例颜色全梁场唯一，应触发颜色重复校验",
   API["add"], H_OK,
   body("测试梁型-颜色重复-A15", "1", "1", 32.6, "${sjthA}", "0", "1", "1", "1", 50, "#8B0000"), None, None)
td("beamtype.add.a15.verify", "回查A15未被创建", "按名称查询，确认因颜色重复被拒绝的记录没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-颜色重复-A15"}, None)

# —— 名称可重复：A17 两条同名，但七项要素与颜色都不同
td("beamtype.add.a17.seed", "新增-同名用例基线A17",
   "T 梁 / 20 米 / 单线 / 无声 / 边梁 / 曲线，图例颜色 #DAA520",
   API["add"], H_OK,
   body("测试梁型-同名测试-A17", "1", "3", 20.6, "${sjthA}", "0", "1", "2", "2", 24, "#DAA520"), None, None)
td("beamtype.add.a17.same_name", "新增-与A17同名但要素不同",
   "名称与 A17 完全相同，但七项要素与图例颜色（#C71585）都不同；名称无唯一校验，应允许新增",
   API["add"], H_OK,
   body("测试梁型-同名测试-A17", "1", "4", 16.6, "${sjthA}", "1", "2", "1", "1", 36, "#C71585"), None, None)
td("beamtype.add.a17.same_name.verify", "回查同名A17共2条",
   "按名称精确查询，应返回 2 条同名记录（要素与颜色不同），并提取第 2 条 btId 供清场",
   API["list"], H_OK, None, {"name": "测试梁型-同名测试-A17"},
   [ex("btIdA17", "$..[?(@.name=='测试梁型-同名测试-A17')].btId", "A17 第 1 条 btId"),
    ex("btIdA17b", "$..[?(@.name=='测试梁型-同名测试-A17')].btId", "A17 第 2 条 btId（同名新增的那条）", 1)])

# 其余新增负向数据（均因必填缺失或鉴权失败被拒，不会落库）
# 关键约束：负向报文若与某条「新增成功」的数据（七项要素 + 图例颜色）重合，系统可能先命中判重/颜色校验，
# 返回的提示语就不再是「缺少必填参数 / 未授权」，AI 断言会误判（甚至把判重误当成必填生效）。
# 因此下面 4 条负向报文各用一套**不与任何落地数据重合**的七项要素 + 图例颜色（末尾有专门的负向数据自检）。
def neg_add(name, body_type, len_type, length, barrier, line, zp, beam_location, plan, color, drop=None):
    b = body(name, body_type, len_type, length, "${sjthA}", barrier, line, zp, beam_location, plan, color)
    if drop:
        b.pop(drop, None)
    return b

td("beamtype.add.miss_name", "新增-缺少name",
   "请求体不含必填字段 name；其余字段用独立组合（箱梁 40.375m 双线 有声 直线 / #1E3A8A），确保不会先命中判重", API["add"], H_OK,
   neg_add("测试梁型-缺名称-A06", "2", "6", 40.375, "1", "2", "1", None, 30, "#1E3A8A", "name"), None, None)
td("beamtype.add.miss_sjth", "新增-缺少sjth",
   "请求体不含必填字段 sjth（通图号）；其余字段用独立组合（箱梁 20m 单线 有声 曲线 / #7C2D12），确保不会先命中判重", API["add"], H_OK,
   neg_add("测试梁型-缺通图号-A07", "2", "3", 20.6, "1", "1", "2", None, 25, "#7C2D12", "sjth"), None, None)
td("beamtype.add.miss_plan_total", "新增-缺少planTotal",
   "请求体不含必填字段 planTotal；其余字段用独立组合（箱梁 20m 单线 无声 曲线 / #0F766E），确保不会先命中判重", API["add"], H_OK,
   neg_add("测试梁型-缺计划-A08", "2", "3", 20.6, "0", "1", "2", None, 20, "#0F766E", "planTotal"), None, None)
td("beamtype.add.miss_color", "新增-缺少beamTypeColor",
   "请求体不含必填字段 beamTypeColor（箱梁同样必填）；其余字段用独立组合（箱梁 40.375m 单线 有声 直线），确保不会先命中判重", API["add"], H_OK,
   neg_add("测试梁型-缺颜色-A09", "2", "6", 40.375, "1", "1", "1", None, 18, None, "beamTypeColor"), None, None)
td("beamtype.add.miss_color.verify", "回查A09未被创建", "按名称查询，确认因缺 beamTypeColor 被拒绝的记录没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-缺颜色-A09"}, None)
td("beamtype.add.miss_location_tbeam", "新增-T梁缺少beamLocation",
   "T 梁（beamBodyType=1）未传条件必填的 beamLocation；其余字段用独立组合（T梁 32m 单线 无声 直线 边梁位 / #8C1D40）", API["add"], H_OK,
   neg_add("测试梁型-缺梁位-A10", "1", "1", 32.6, "0", "1", "1", None, 36, "#8C1D40"), None, None)
td("beamtype.add.miss_location_tbeam.verify", "回查A10未被创建", "按名称查询，确认因 T 梁缺 beamLocation 被拒绝的记录没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-缺梁位-A10"}, None)
td("beamtype.add.no_auth", "新增-缺少Authorization", "请求头只带 Sys-dept-id，不带 Authorization；数据用独立组合（T梁 32m 双线 无声 曲线 中梁 / #155E75）", API["add"], H_NO_AUTH,
   neg_add("测试梁型-未授权新增-A11", "1", "1", 32.6, "0", "2", "2", "1", 60, "#155E75"), None, None)
td("beamtype.add.no_auth.verify", "回查A11未被创建", "按名称查询，确认鉴权失败的记录没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-未授权新增-A11"}, None)
td("beamtype.add.no_dept", "新增-缺少Sys-dept-id", "请求头只带 Authorization，不带梁场标识；数据用独立组合（箱梁 20m 双线 无声 曲线 / #0B4F6C），不得与 A01 撞车", API["add"], H_NO_DEPT,
   neg_add("测试梁型-缺部门标识-A12", "2", "3", 20.6, "0", "2", "2", None, 24, "#0B4F6C"), None, None)
td("beamtype.add.no_dept.verify", "回查A12未被创建", "按名称查询，确认缺少部门标识的请求没有落库", API["list"], H_OK,
   None, {"name": "测试梁型-缺部门标识-A12"}, None)
td("beamtype.add.sql_inject", "新增-名称含SQL注入payload",
   "name 塞入 ' OR 1=1 -- 类注入片段（无单引号变体，避免污染 JSONPath）；其余字段取自「20m 双线 / 无声 / 曲线」组合，与其它造数不重复",
   API["add"], H_OK,
   body("测试梁型-A13 OR 1=1 --", "2", "3", 20.6, "${sjthA}", "0", "2", "2", None, 90, "#9932CC"), None, None)
td("beamtype.add.sql_inject.verify", "回查注入名称落库形态", "按名称查询，确认注入片段按普通字符串处理、库表未被破坏", API["list"], H_OK,
   None, {"name": "测试梁型-A13 OR 1=1 --"}, [ex("btIdA13", "$..[?(@.name=='测试梁型-A13 OR 1=1 --')].btId", "A13 的 btId（若被落库）")])

# 列表 / 分页 / 通过id查询 / 编辑 / 删除 / 批量删除用例的造数见上表（ADDS）

# 编辑用例的数据（btId 为必填主键；编辑后的组合也必须与其它记录不重复，见末尾自检）
# 负向编辑报文的七项要素与颜色同样刻意避开所有落地数据，否则可能先被判重/颜色校验拦截，
# 返回的提示语就不是「缺少必填 / 未授权」，AI 断言会误判。
def upd(name, body_type, len_type, length, sjth, barrier, line, zp, beam_location, plan, color,
        bt_id, drop=None):
    b = body(name, body_type, len_type, length, sjth, barrier, line, zp, beam_location, plan, color)
    if drop:
        b.pop(drop, None)
    return dict({"btId": bt_id}, **b)


td("beamtype.update.u01", "编辑U01-全字段修改",
   "btId=${btIdU01}；改名 + 跨度 32.6→32.2 + 声屏障/线型/线形/计划数量/图例颜色全改，sjth 保持不变",
   API["update"], H_OK,
   upd("测试梁型-32m单线箱梁-U01已改", "2", "1", 32.2, "${sjthG}", "0", "1", "2", None, 88, "#CD5C5C",
       "${btIdU01}"), None, None)
td("beamtype.update.u01.verify", "回查U01修改结果", "按 btId 回查，逐字段比对", API["get"], H_OK, None, {"btId": "${btIdU01}"}, None)
td("beamtype.update.u02", "编辑U02-更换通图号", "btId=${btIdU02}；sjth 由 ${sjthG} 更换为 ${sjthB}，其余字段原样回传", API["update"], H_OK,
   upd("测试梁型-24m单线T梁-U02", "1", "2", 24.6, "${sjthB}", "1", "1", "2", "3", 64, "#DC143C",
       "${btIdU02}"), None, None)
td("beamtype.update.u02.verify", "回查U02通图号", "按 btId 回查，确认 sjth 已变为另一条通图号的 bddId", API["get"], H_OK, None,
   {"btId": "${btIdU02}"}, None)
td("beamtype.update.u03", "编辑U03-梁位置中梁改边梁", "btId=${btIdU03}；beamLocation 1（中梁）→ 2（边梁）", API["update"], H_OK,
   upd("测试梁型-20m双线T梁-U03", "1", "3", 20.6, "${sjthG}", "0", "2", "1", "2", 64, "#E9967A",
       "${btIdU03}"), None, None)
td("beamtype.update.u03.verify", "回查U03梁位置", "按 btId 回查 beamLocation", API["get"], H_OK, None, {"btId": "${btIdU03}"}, None)
td("beamtype.update.u04.miss_name", "编辑U04-缺少name",
   "btId 正确但不传 name；其余字段用独立组合（箱梁 16m 单线 有声 曲线 / #7A1F3D），避免被判重抢先拦截", API["update"], H_OK,
   upd("测试梁型-32m单线箱梁-U04", "2", "4", 16.6, "${sjthG}", "1", "1", "2", None, 100, "#7A1F3D",
       "${btIdU04}", "name"), None, None)
td("beamtype.update.u04.verify", "回查U04未被修改", "按 btId 回查，名称应仍为原值", API["get"], H_OK, None, {"btId": "${btIdU04}"}, None)
td("beamtype.update.not_exist", "编辑-主键不存在",
   "btId=not_exist_bt_id_99999，其余字段用独立组合（箱梁 16m 双线 有声 直线 / #3D0C11），不会被判重掩盖真实结果", API["update"], H_OK,
   upd("测试梁型-不存在主键-U00", "2", "4", 16.6, "${sjthG}", "1", "2", "1", None, 10, "#3D0C11",
       "not_exist_bt_id_99999"), None, None)
td("beamtype.update.u06.no_dept", "编辑U06-缺少Sys-dept-id",
   "请求头只带 Authorization，名称改为「测试梁型-越权修改-U06」；数据用独立组合（箱梁 16m 单线 无声 直线 / #0E3B2E）", API["update"], H_NO_DEPT,
   upd("测试梁型-越权修改-U06", "2", "4", 16.6, "${sjthG}", "0", "1", "1", None, 100, "#0E3B2E",
       "${btIdU06}"), None, None)
td("beamtype.update.u06.verify", "回查U06未被越权修改", "用正常请求头按 btId 回查，名称应仍为原值", API["get"], H_OK, None,
   {"btId": "${btIdU06}"}, None)
td("beamtype.update.u07.no_auth", "编辑U07-缺少Authorization",
   "请求头只带 Sys-dept-id，名称改为「测试梁型-无令牌修改-U07」；数据用独立组合（T梁 16m 单线 无声 曲线 中梁 / #5B2A86）", API["update"], H_NO_AUTH,
   upd("测试梁型-无令牌修改-U07", "1", "4", 16.6, "${sjthG}", "0", "1", "2", "1", 100, "#5B2A86",
       "${btIdU07}"), None, None)
td("beamtype.update.u07.verify", "回查U07未被修改", "用正常请求头按 btId 回查，名称应仍为原值", API["get"], H_OK, None,
   {"btId": "${btIdU07}"}, None)

# 删除用例的数据
td("beamtype.delete.d01", "通过id删除-D01", "btId=${btIdD01}", API["del"], H_OK, None, {"btId": "${btIdD01}"}, None)
td("beamtype.delete.d02.no_auth", "通过id删除D02-缺少Authorization", "请求头只带 Sys-dept-id", API["del"], H_NO_AUTH, None,
   {"btId": "${btIdD02}"}, None)
td("beamtype.delete.d03.first", "通过id删除D03-第1次", "", API["del"], H_OK, None, {"btId": "${btIdD03}"}, None)
td("beamtype.delete.d03.second", "通过id删除D03-第2次", "对同一 btId 重复删除", API["del"], H_OK, None, {"btId": "${btIdD03}"}, None)
td("beamtype.delete.not_exist", "通过id删除-主键不存在", "btId=not_exist_bt_id_99999", API["del"], H_OK, None,
   {"btId": "not_exist_bt_id_99999"}, None)
td("beamtype.delete.miss_param", "通过id删除-缺少btId", "不传 btId", API["del"], H_OK, None, {}, None)

td("beamtype.delete.batch.b01_b02", "批量删除B01,B02", "btIds=${btIdB01},${btIdB02}", API["batch"], H_OK, None,
   {"btIds": "${btIdB01},${btIdB02}"}, None)
td("beamtype.delete.batch.miss_param", "批量删除-缺少btIds", "不传 btIds", API["batch"], H_OK, None, {}, None)
td("beamtype.delete.batch.mixed", "批量删除-有效ID+无效ID", "btIds=${btIdB03},not_exist_bt_id_99999", API["batch"], H_OK, None,
   {"btIds": "${btIdB03},not_exist_bt_id_99999"}, None)
td("beamtype.delete.batch.b04_b05.no_auth", "批量删除B04,B05-缺少Authorization", "请求头只带 Sys-dept-id", API["batch"], H_NO_AUTH,
   None, {"btIds": "${btIdB04},${btIdB05}"}, None)

# 查询类数据
td("beamtype.query.list.all", "列表查询-无参", "不带任何过滤条件查询本梁场梁型列表", API["list"], H_OK, None, None, None)
td("beamtype.query.list.by_name", "列表查询-按名称", "name=测试梁型-24m单线T梁-Q02", API["list"], H_OK, None,
   {"name": "测试梁型-24m单线T梁-Q02"}, None)
td("beamtype.query.list.by_name_fuzzy", "列表查询-按名称模糊匹配", "name=测试梁型-模糊匹配（前缀，应命中 F01 与 F02）", API["list"], H_OK, None,
   {"name": "测试梁型-模糊匹配"}, None)
td("beamtype.query.list.by_sjth", "列表查询-按通图号", "sjth 取 Q03 独占的第 3 条通图号（${sjthC}），该通图号下只有 Q03 一条梁型", API["list"], H_OK, None,
   {"sjth": "${sjthC}"}, None)
td("beamtype.query.list.by_body_type", "列表查询-按梁体类型", "beamBodyType=2（箱梁）", API["list"], H_OK, None,
   {"beamBodyType": "2"}, None)
td("beamtype.query.list.no_match", "列表查询-无匹配", "name 传入不存在的名称", API["list"], H_OK, None,
   {"name": "不存在的梁型名称-000000"}, None)
td("beamtype.query.list.no_auth", "列表查询-缺少Authorization", "请求头只带 Sys-dept-id", API["list"], H_NO_AUTH, None, None, None)
td("beamtype.query.list.no_dept", "列表查询-缺少Sys-dept-id", "请求头只带 Authorization", API["list"], H_NO_DEPT, None, None, None)
td("beamtype.query.list.fake_dept", "列表查询-不存在的梁场标识", "Sys-dept-id=999999999", API["list"], H_FAKE_DEPT, None, None, None)

# 分页数据
td("beamtype.query.page.default", "分页查询-第1页10条", "pageNum=1&pageSize=10", API["page"], H_OK, None,
   {"pageNum": 1, "pageSize": 10}, None)
td("beamtype.query.page.size1", "分页查询-每页1条", "pageNum=1&pageSize=1", API["page"], H_OK, None,
   {"pageNum": 1, "pageSize": 1}, None)
td("beamtype.query.page.second", "分页查询-第2页", "pageNum=2&pageSize=1", API["page"], H_OK, None,
   {"pageNum": 2, "pageSize": 1}, None)
td("beamtype.query.page.invalid", "分页查询-非法参数", "pageNum=0&pageSize=-1", API["page"], H_OK, None,
   {"pageNum": 0, "pageSize": -1}, None)
td("beamtype.query.page.no_auth", "分页查询-缺少Authorization", "请求头只带 Sys-dept-id", API["page"], H_NO_AUTH, None,
   {"pageNum": 1, "pageSize": 10}, None)

# 通过id查询数据
td("beamtype.query.by_id", "通过id查询-G01", "btId=${btIdG01}", API["get"], H_OK, None, {"btId": "${btIdG01}"}, None)
td("beamtype.query.by_id.not_exist", "通过id查询-主键不存在", "btId=not_exist_bt_id_99999", API["get"], H_OK, None,
   {"btId": "not_exist_bt_id_99999"}, None)
td("beamtype.query.by_id.miss_param", "通过id查询-缺少btId", "不传 btId", API["get"], H_OK, None, {}, None)

# ---------------------------------------------------------------- 2. 用例
SUB_ADD = "新增"
SUB_LIST = "列表查询"
SUB_PAGE = "分页列表查询"
SUB_GET = "通过id查询"
SUB_UPD = "编辑"
SUB_DEL = "通过id删除"
SUB_BATCH = "批量删除"
SUB_CLN = "清场"
SUB_BASE = "基础数据"


def verify_by_name(key, name, extra=None, ai=None, desc=None):
    rules = [r("$", "res_contains_data", {"status": "1", "code": "200"}),
             r("$.data", "type", "list"),
             r("$.data", "length_gt", 0),
             r("$.data[0].name", "eq", name)]
    if extra:
        rules += extra
    return S(key, desc or f"GET 列表查询 name={name}，回查落库结果", A(rules, ai))


def verify_by_id(key, extra=None, ai=None, desc=None):
    rules = [r("$", "res_contains_data", {"status": "1", "code": "200"}),
             r("$.data", "res_contains_key", BT_KEYS),
             r("$.data.btId", "not_empty")]
    if extra:
        rules += extra
    return S(key, desc or "GET 通过id查询，回查修改结果", A(rules, ai))


# ---- 新增
case("beamtype.add.box32_success", SUB_ADD, "新增32m双线箱梁成功且列表可查（sjth 取通图号 bddId）",
     "TC-BT-501: 新增 2 箱梁 / 32 米 / 双线 / 有声屏障 / 直线的梁型，sjth 直接取通图号列表第一条的 bddId。校验新增成功，并按名称回查确认 9 个必填字段与图例颜色全部落库，同时提取 btId 供后续断言使用。本用例数据保留至模块最后一条用例统一清场",
     [S("beamtype.add.a01", "POST 新增 A01，请求头 Sys-dept-id=${bfDeptId}，sjth=${sjthA}", OK),
      verify_by_name("beamtype.by_name.a01", "测试梁型-32m双线箱梁-A01",
                     [r("$.data[0].beamBodyType", "eq", "2"),
                      r("$.data[0].beamLengthType", "eq", "1"),
                      r("$.data[0].beamLength", "in", [32.6, "32.6"]),
                      r("$.data[0].sjth", "eq_req_body_jsonpath", "$.sjth"),
                      r("$.data[0].barrierType", "eq", "1"),
                      r("$.data[0].lineType", "eq", "2"),
                      r("$.data[0].zpType", "eq", "1"),
                      r("$.data[0].planTotal", "in", [120, "120"]),
                      r("$.data[0].beamTypeColor", "eq", "#1F6FD0")],
                     "回查的 sjth 必须与新增报文里的 sjth（通图号 bddId）完全一致，说明存的是取到的通图号而不是占位值或空串"),
      ])

case("beamtype.add.tbeam24_success", SUB_ADD, "新增24m单线T梁（中梁）成功且beamLocation落库",
     "TC-BT-502: 新增 1 T梁 / 24 米 / 单线 / 无声屏障 / 曲线 / 中梁。T 梁必须带 T 型梁位置，校验 beamLocation=1（中梁）与其余枚举字段均正确落库",
     [S("beamtype.add.a02", "POST 新增 A02，beamBodyType=1、beamLocation=1", OK),
      verify_by_name("beamtype.by_name.a02", "测试梁型-24m单线T梁-A02",
                     [r("$.data[0].beamBodyType", "eq", "1"),
                      r("$.data[0].beamLengthType", "eq", "2"),
                      r("$.data[0].beamLength", "in", [24.6, "24.6"]),
                      r("$.data[0].barrierType", "eq", "0"),
                      r("$.data[0].lineType", "eq", "1"),
                      r("$.data[0].zpType", "eq", "2"),
                      r("$.data[0].beamLocation", "eq", "1"),
                      r("$.data[0].sjth", "eq_req_body_jsonpath", "$.sjth"),
                      r("$.data[0].planTotal", "in", [64, "64"])])])

case("beamtype.add.required_only", SUB_ADD, "仅传必填字段新增成功（箱梁可不传 beamLocation）",
     "TC-BT-503: 只回传 10 个必填字段（name/beamBodyType/beamLengthType/beamLength/sjth/barrierType/lineType/zpType/planTotal/beamTypeColor）。"
     "beamLocation 为条件必填，仅 T 梁需要；本用例是箱梁，不传 T 型梁位置也应新增成功，并校验图例颜色已落库",
     [S("beamtype.add.a03", "POST 新增 A03（箱梁 20m 单线 无声 直线），只传 10 个必填字段、不传 beamLocation", OK),
      verify_by_name("beamtype.by_name.a03", "测试梁型-20m仅必填-A03",
                     [r("$.data[0].beamBodyType", "eq", "2"),
                      r("$.data[0].beamLengthType", "eq", "3"),
                      r("$.data[0].sjth", "eq_req_body_jsonpath", "$.sjth"),
                      r("$.data[0].planTotal", "in", [40, "40"]),
                      r("$.data[0].beamTypeColor", "eq", "#4C1D95")],
                     "箱梁不传 beamLocation 应允许新增；beamTypeColor 为必填项，回查颜色必须与报文一致")])

case("beamtype.add.boundary_length", SUB_ADD, "跨度三位小数与最小计划数量边界值新增成功",
     "TC-BT-504: beamLengthType=6（其他）、beamLength=40.375（三位小数）、planTotal=1（最小值），校验数值精度与边界值不被截断",
     [S("beamtype.add.a04", "POST 新增 A04，beamLength=40.375、planTotal=1", OK),
      verify_by_name("beamtype.by_name.a04", "测试梁型-40m其他-A04",
                     [r("$.data[0].beamLengthType", "eq", "6"),
                      r("$.data[0].sjth", "eq_req_body_jsonpath", "$.sjth"),
                      r("$.data[0].beamLength", "in", [40.375, "40.375"]),
                      r("$.data[0].planTotal", "in", [1, "1"])])])

case("beamtype.add.dup_combo", SUB_ADD, "七项要素完全相同的梁型重复新增被拒绝",
     "TC-BT-505: 系统判重规则为「梁体类型 + 长度类型 + 通图号 + 正线类型 + 声屏障 + T梁位置 + 直曲类别」七项全同即视为重复。"
     "前置确保基线 A05 存在（没有才新增），再用与其七项完全相同、但名称（A14）与图例颜色都不同的报文新增，应被判重拒绝；回查确认未落库",
     [S("beamtype.add.a05.dup", "POST 新增 A14：七项要素与 A05 全同，仅名称与颜色不同",
        FAIL("message 应提示梁型重复（梁体类型/长度类型/通图号/正线类型/声屏障/T梁位置/直曲类别已存在），不应静默成功")),
      S("beamtype.add.a05.dup.verify", "GET 列表查询 name=A14，确认未创建",
        OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.probe.a05.seed", "beamtype.add.a05.seed")])

case("beamtype.add.dup_color", SUB_ADD, "架设图例颜色重复新增被拒绝（全梁场唯一，跨梁体类型）",
     "TC-BT-505B: 架设图例颜色在全梁场范围内唯一，不同梁体类型也不能复用同一颜色。前置确保基线 A16（箱梁，颜色 #8B0000）存在（没有才新增），"
     "再用七项要素全部不同、梁体类型也不同（T 梁）、但图例颜色同为 #8B0000 的报文新增 A15，应被颜色重复校验拒绝；回查确认未落库。"
     "该用例刻意跨梁体类型，可区分「全梁场唯一」与「同一梁体类型内唯一」两种实现",
     [S("beamtype.add.a15.dup_color", "POST 新增 A15（T梁 32m）：梁体类型与各项要素均不同，仅颜色与 A16 相同",
        FAIL("message 应提示架设图例颜色重复（该颜色已被其它梁型占用），不应因梁体类型不同而放行")),
      S("beamtype.add.a15.verify", "GET 列表查询 name=A15，确认未创建",
        OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.probe.a16.seed", "beamtype.add.a16.seed")])

case("beamtype.add.same_name", SUB_ADD, "同名但七项要素与颜色均不同的梁型可正常新增",
     "TC-BT-505C: 梁型名称没有唯一性校验，判重只看七项要素 + 图例颜色。前置确保 A17 存在（没有才新增），"
     "再用同名、但七项要素与颜色都不同的报文新增，应成功；按名称精确回查应返回 2 条同名记录",
     [S("beamtype.add.a17.same_name", "POST 新增第二条同名 A17（T梁 16m 双线 中梁 直线，颜色 #C71585）", OK),
      S("beamtype.add.a17.same_name.verify", "GET 列表查询 name=测试梁型-同名测试-A17，确认存在 2 条",
        OKX([r("$.data", "length_eq", 2),
             r("$.data[0].name", "eq", "测试梁型-同名测试-A17")],
            "名称不做唯一校验，同名记录应共有 2 条，且两条的图例颜色不同"))],
     seeds=[("beamtype.probe.a17.seed", "beamtype.add.a17.seed")])

MISS = "message 应明确提示缺少必填参数（字段名或“不能为空”类提示），不得返回内部异常"
# 负向用例的报文刻意使用独立组合，避免被「梁型重复 / 颜色重复」抢先拦截，导致提示语不是必填缺失
MISS_NOTE = "（其余字段为独立组合，不与任何新增成功的数据撞判重七项要素或图例颜色）"

case("beamtype.add.miss_name", SUB_ADD, "缺少必填字段name新增失败",
     "TC-BT-506: 请求体不含 name，其余字段齐全；" + MISS_NOTE + "，必填校验应拦截",
     [S("beamtype.add.miss_name", "POST 新增，body 无 name（箱梁 40.375m 双线 有声 直线 / #1E3A8A）", FAIL(MISS))])
case("beamtype.add.miss_sjth", SUB_ADD, "缺少必填字段sjth（通图号）新增失败",
     "TC-BT-507: 请求体不含 sjth，必填校验应拦截（sjth 必须来自通图号 bddId）；" + MISS_NOTE,
     [S("beamtype.add.miss_sjth", "POST 新增，body 无 sjth（箱梁 20m 单线 有声 曲线 / #7C2D12）", FAIL(MISS))])
case("beamtype.add.miss_plan_total", SUB_ADD, "缺少必填字段planTotal新增失败",
     "TC-BT-508: 请求体不含 planTotal，必填校验应拦截；" + MISS_NOTE,
     [S("beamtype.add.miss_plan_total", "POST 新增，body 无 planTotal（箱梁 20m 单线 无声 曲线 / #0F766E）", FAIL(MISS))])
case("beamtype.add.miss_color", SUB_ADD, "缺少必填字段beamTypeColor（架设图例颜色）新增失败",
     "TC-BT-508B: beamTypeColor 为必填项，不传应被必填校验拦截（箱梁场景同样不能省略）；" + MISS_NOTE,
     [S("beamtype.add.miss_color", "POST 新增 A09（箱梁 40.375m 单线 有声 直线），body 无 beamTypeColor", FAIL(MISS)),
      S("beamtype.add.miss_color.verify", "GET 列表查询 name=A09，确认未创建",
        OKX([r("$.data", "is_empty")]))])
case("beamtype.add.miss_location_tbeam", SUB_ADD, "T梁缺少beamLocation新增失败（beamLocation 为条件必填）",
     "TC-BT-508C: beamLocation 是条件必填——T 梁（beamBodyType=1）必须传 T 型梁位置，箱梁（beamBodyType=2）可不传。"
     "本用例用 T 梁报文但不传 beamLocation，应被必填校验拦截并断言未落库；箱梁可缺席的正向场景由「仅传必填字段新增成功」用例覆盖",
     [S("beamtype.add.miss_location_tbeam", "POST 新增 A10（T梁 32m 单线 无声 直线），body 无 beamLocation", FAIL(MISS)),
      S("beamtype.add.miss_location_tbeam.verify", "GET 列表查询 name=A10，确认未创建",
        OKX([r("$.data", "is_empty")]))])
case("beamtype.add.no_auth", SUB_ADD, "缺少Authorization新增梁型鉴权失败且未落库",
     "TC-BT-511: 请求头只带 Sys-dept-id，不带 Authorization，应鉴权失败；随后用正常令牌按名称回查，确认记录未被创建",
     [S("beamtype.add.no_auth", "POST 新增 A11，请求头仅 Sys-dept-id", NO_AUTH()),
      S("beamtype.add.no_auth.verify", "GET 列表查询 name=A11，确认未创建",
        OKX([r("$.data", "is_empty")]))])

case("beamtype.add.no_dept", SUB_ADD, "缺少Sys-dept-id新增梁型被拒绝且未落库",
     "TC-BT-512: 请求头只带 Authorization，不带梁场标识 Sys-dept-id，接口无法确定所属梁场，应拒绝执行；回查确认未创建",
     [S("beamtype.add.no_dept", "POST 新增 A12，请求头仅 Authorization", FAIL("缺少 Sys-dept-id 时应拒绝执行，提示缺少部门标识 / 未授权类信息")),
      S("beamtype.add.no_dept.verify", "GET 列表查询 name=A12，确认未创建",
        OKX([r("$.data", "is_empty")]))])

case("beamtype.add.sql_inject", SUB_ADD, "梁型名称含SQL注入payload不产生注入风险",
     "TC-BT-513: name 传入「测试梁型-A13 OR 1=1 --」，校验接口不返回 500、库表未被破坏，注入片段按普通字符串处理或直接拒绝",
     [S("beamtype.add.sql_inject", "POST 新增，name 含 SQL 注入片段",
        A([r("$.code", "eq", "200")], "接口不得返回 500 或数据库异常；注入片段应作为普通字符串落库（或按命名规则直接拒绝），不得影响既有数据")),
      S("beamtype.add.sql_inject.verify", "GET 列表查询注入名称，确认列表接口仍可正常工作",
        A([r("$", "res_contains_data", {"status": "1", "code": "200"}), r("$.data", "type", "list")],
          "列表接口应正常工作且不报数据库异常；若新增被拒绝则返回空数组，若落库则名称原样回显")),
      ])

# ---- 列表查询
case("beamtype.query.list_success", SUB_LIST, "不带条件查询梁型列表成功且字段齐全",
     "TC-BT-520: 前置确保源数据 Q01 存在（**没有才新增**，已有则直接复用），再不带任何 query 参数查询，"
     "校验 data 为数组、至少 1 条、首条包含 12 个业务字段",
     [S("beamtype.query.list.all", "GET 列表查询，不带 query 参数",
        A([r("$", "res_contains_data", {"status": "1", "code": "200"}),
           r("$.data", "type", "list"),
           r("$.data", "length_gt", 0),
           r("$.data[0]", "res_contains_key", BT_KEYS)]))],
     seeds=[("beamtype.probe.q01", "beamtype.add.q01")])

case("beamtype.query.list_by_name", SUB_LIST, "按梁型名称过滤查询命中目标记录",
     "TC-BT-521: 前置确保源数据 Q02 存在（没有才新增），按完整名称查询（name 为模糊匹配，完整名称同样命中），"
     "校验返回项名称与查询条件一致",
     [verify_by_name("beamtype.query.list.by_name", "测试梁型-24m单线T梁-Q02",
                     [r("$.data[0].beamBodyType", "eq", "1"),
                      r("$.data[0].beamLocation", "eq", "2")],
                     desc="GET 列表查询 name=Q02")],
     seeds=[("beamtype.probe.q02", "beamtype.add.q02")])

case("beamtype.query.list_by_name_fuzzy", SUB_LIST, "按名称模糊匹配返回全部包含关键字的梁型",
     "TC-BT-521B: name 为模糊匹配。前置确保 2 条名称共享前缀「测试梁型-模糊匹配」的源数据 F01、F02 存在（各自没有才新增），"
     "再用该前缀查询，校验返回至少 2 条且首条名称包含该关键字（名称与该关键字无关的记录不得混入）",
     [S("beamtype.query.list.by_name_fuzzy", "GET 列表查询 name=测试梁型-模糊匹配",
        OKX([r("$.data", "type", "list"),
             r("$.data", "length_gt", 1),
             r("$.data[0].name", "contains", "测试梁型-模糊匹配")],
            "模糊匹配应返回所有名称包含「测试梁型-模糊匹配」的梁型（至少 F01、F02 两条），不应把名称不含该关键字的记录混进来"))],
     seeds=[("beamtype.probe.f01", "beamtype.add.f01"),
            ("beamtype.probe.f02", "beamtype.add.f02")])

case("beamtype.query.list_by_sjth", SUB_LIST, "按通图号sjth过滤查询",
     "TC-BT-522: 前置确保源数据 Q03 存在（没有才新增）后按 sjth 过滤。Q03 独占第 3 条通图号 ${sjthC}，该通图号下只有这一条梁型，"
     "因此可断言返回恰好 1 条、且 sjth 等于筛选值，能真正验证「按通图号过滤生效」而不只是「查得到东西」。"
     "断言用 eq 比对上下文变量 sjthC（通图号列表接口提取的 bddId，ctx.is_ctx_var=True 标记为上下文变量、执行时自动替换）："
     "造数已移到前置，库里本来就有 Q03 时不会新增，本用例的测试步骤里没有新增报文可比，eq_req_body_jsonpath 取不到值",
     [S("beamtype.query.list.by_sjth", "GET 列表查询 sjth=${sjthC}",
        OKX([r("$.data", "type", "list"),
             r("$.data", "length_eq", 1),
             rv("$.data[0].sjth", "eq", "sjthC"),
             r("$.data[0].name", "eq", "测试梁型-24m单线箱梁-Q03"),
             r("$.data[0].beamBodyType", "eq", "2")],
            "该通图号下只有 Q03 一条记录：应恰好返回 1 条，且 sjth 与筛选值（上下文变量 sjthC）一致；"
            "若返回多条或串入其它通图号的梁型，说明过滤未生效"))],
     seeds=[("beamtype.probe.q03", "beamtype.add.q03")])

case("beamtype.query.list_by_body_type", SUB_LIST, "按梁体类型过滤查询",
     "TC-BT-523: 前置确保箱梁源数据 Q05 存在（没有才新增）后按 beamBodyType=2（箱梁）过滤，"
     "校验命中且返回项梁体类型均为 2，不混入 T 梁",
     [S("beamtype.query.list.by_body_type", "GET 列表查询 beamBodyType=2",
        OKX([r("$.data", "type", "list"),
             r("$.data", "length_gt", 0),
             r("$.data[0].beamBodyType", "eq", "2")],
            "返回项的 beamBodyType 应全部为 2（箱梁），不应混入 T 梁"))],
     seeds=[("beamtype.probe.q05", "beamtype.add.q05")])

case("beamtype.query.list_no_match", SUB_LIST, "查询不存在的梁型名称返回空数组",
     "TC-BT-524: name 传入不存在的名称，应返回成功 + 空数组，不得报错",
     [S("beamtype.query.list.no_match", "GET 列表查询 name=不存在的梁型名称-000000",
        OKX([r("$.data", "is_empty")]))])

case("beamtype.query.list_no_auth", SUB_LIST, "缺少Authorization查询梁型列表鉴权失败",
     "TC-BT-525: 请求头只带 Sys-dept-id，不带 Authorization，应鉴权失败且不返回梁型数据",
     [S("beamtype.query.list.no_auth", "GET 列表查询，请求头仅 Sys-dept-id",
        A([r("$.status", "ne", "1"), r("$.data", "is_empty")]))])

case("beamtype.query.list_no_dept", SUB_LIST, "缺少Sys-dept-id查询不返回任何梁型数据",
     "TC-BT-526: 请求头只带 Authorization，接口无法定位梁场，应返回空列表或业务提示，且不得串出其它梁场的数据",
     [S("beamtype.query.list.no_dept", "GET 列表查询，请求头仅 Authorization",
        A([r("$..btId", "is_empty")],
          "缺少 Sys-dept-id 时应返回空列表或“梁场/部门不存在”类提示，不得返回任何梁型数据，也不得抛内部异常"))])

case("beamtype.query.list_fake_dept", SUB_LIST, "Sys-dept-id为不存在的梁场时不串出其它梁场数据",
     "TC-BT-527: 请求头 Sys-dept-id=999999999（库中不存在的 deptId），校验不报内部异常且不返回任何梁型数据",
     [S("beamtype.query.list.fake_dept", "GET 列表查询，Sys-dept-id=999999999",
        A([r("$..btId", "is_empty")],
          "梁场标识不存在时应返回空列表或业务提示，不得返回其它梁场的梁型数据，也不得抛数据库/内部异常"))])

# ---- 分页
page_ok_rules = [
    r("$.data", "res_contains_key", ["total", "list", "pageNum", "pageSize", "pages", "isFirstPage", "isLastPage"]),
    r("$.data.total", "gte", 1),
    r("$.data.pageNum", "in", [1, "1"]),
    r("$.data.pageSize", "in", [10, "10"]),
    r("$.data.list", "type", "list"),
    r("$.data.list", "length_gt", 0),
    r("$.data.isFirstPage", "in", [True, "true", 1]),
]
case("beamtype.query.page_success", SUB_PAGE, "分页查询第1页10条返回结构正确",
     "TC-BT-530: 前置确保源数据 P01 存在（没有才新增）后按 pageNum=1&pageSize=10 查询，"
     "校验分页结构（total/list/pageNum/pageSize/pages）存在且 list 非空",
     [S("beamtype.query.page.default", "GET 分页查询 pageNum=1&pageSize=10", OKX(page_ok_rules))],
     seeds=[("beamtype.probe.p01", "beamtype.add.p01")])

case("beamtype.query.page_size_one", SUB_PAGE, "每页1条时分页返回仅1条记录",
     "TC-BT-531: 前置确保独立源数据 P03 存在（没有才新增；不复用 P02A，避免两条用例共用一条新增数据）后按 pageNum=1&pageSize=1 查询，"
     "校验 list 长度恰为 1 且 pageSize=1、isFirstPage=true",
     [S("beamtype.query.page.size1", "GET 分页查询 pageNum=1&pageSize=1",
        OKX([r("$.data.pageSize", "in", [1, "1"]),
             r("$.data.list", "length_eq", 1),
             r("$.data.isFirstPage", "in", [True, "true", 1])]))],
     seeds=[("beamtype.probe.p03", "beamtype.add.p03")])

case("beamtype.query.page_second", SUB_PAGE, "第2页翻页正确且首页标记为false",
     "TC-BT-532: 前置确保 2 条源数据 P02A/P02B 存在（各自没有才新增）后按 pageNum=2&pageSize=1 查询，"
     "校验返回 1 条、isFirstPage=false、hasPreviousPage=true",
     [S("beamtype.query.page.second", "GET 分页查询 pageNum=2&pageSize=1",
        OKX([r("$.data.list", "length_eq", 1),
             r("$.data.pageNum", "in", [2, "2"]),
             r("$.data.isFirstPage", "in", [False, "false", 0]),
             r("$.data.hasPreviousPage", "in", [True, "true", 1])]))],
     seeds=[("beamtype.probe.p02a", "beamtype.add.p02a"),
            ("beamtype.probe.p02b", "beamtype.add.p02b")])

case("beamtype.query.page_invalid", SUB_PAGE, "分页参数非法时不报500",
     "TC-BT-533: pageNum=0、pageSize=-1，校验接口按默认值回退或返回参数校验提示，不得 500",
     [S("beamtype.query.page.invalid", "GET 分页查询 pageNum=0&pageSize=-1",
        A([r("$.code", "eq", "200")],
          "参数非法时应回退默认分页值或返回参数校验提示（status=0），不得抛 500 / 数据库异常"))])

case("beamtype.query.page_no_auth", SUB_PAGE, "缺少Authorization分页查询鉴权失败",
     "TC-BT-534: 请求头只带 Sys-dept-id 进行分页查询，应鉴权失败",
     [S("beamtype.query.page.no_auth", "GET 分页查询，请求头仅 Sys-dept-id", NO_AUTH())])

# ---- 通过id查询
case("beamtype.get.by_id_success", SUB_GET, "通过btId查询单个梁型字段完整正确",
     "TC-BT-540: 前置确保源数据 G01 存在并取回 btId（没有才新增，新增后再查一次取主键），"
     "按 id 查询，逐项校验 12 个业务字段与新增报文一致。造数在前置，测试步骤里没有新增报文，"
     "因此 sjth 用上下文变量 sjthF 做期望值（ctx.is_ctx_var=True，同一份通图号，等价于比对报文里的 sjth）",
     [verify_by_id("beamtype.query.by_id",
                  [r("$.data.name", "eq", "测试梁型-32m双线箱梁-G01"),
                   r("$.data.beamBodyType", "eq", "2"),
                   r("$.data.beamLengthType", "eq", "1"),
                   r("$.data.beamLength", "in", [32.6, "32.6"]),
                   rv("$.data.sjth", "eq", "sjthF"),
                   r("$.data.barrierType", "eq", "0"),
                   r("$.data.lineType", "eq", "2"),
                   r("$.data.zpType", "eq", "2"),
                   r("$.data.planTotal", "in", [100, "100"]),
                   r("$.data.beamTypeColor", "eq", "#4682B4")],
                  desc="GET 通过id查询 btId=${btIdG01}")],
     seeds=[("beamtype.by_name.g01", "beamtype.add.g01", True)])

case("beamtype.get.not_exist", SUB_GET, "btId不存在时返回业务失败而非异常",
     "TC-BT-541: btId=not_exist_bt_id_99999，校验返回业务提示（数据不存在/已删除），不得 500 且不得返回其它梁型",
     [S("beamtype.query.by_id.not_exist", "GET 通过id查询，btId 不存在",
        A([r("$.code", "eq", "200")],
          "应返回“数据不存在/已删除”类业务提示（status=0），不得返回 500 或其它梁型的数据"))])

case("beamtype.get.miss_param", SUB_GET, "缺少必填参数btId查询失败",
     "TC-BT-542: 不传 btId，必填校验应拦截",
     [S("beamtype.query.by_id.miss_param", "GET 通过id查询，不传 btId", FAIL(MISS))])

# ---- 编辑
case("beamtype.update.success", SUB_UPD, "全字段修改梁型成功且逐项回查一致",
     "TC-BT-550: 前置确保源数据 U01 存在并取回 btId（没有才新增）后全量回传 13 个字段（含必填主键 btId），"
     "改名并修改跨度/声屏障/线型/线形/计划数量/图例颜色，sjth 保持不变；按 btId 回查逐项比对",
     [S("beamtype.update.u01", "POST 编辑 U01：名称改为「测试梁型-32m单线箱梁-U01已改」，beamLength=32.2", OK),
      verify_by_id("beamtype.update.u01.verify",
                   [r("$.data.name", "eq", "测试梁型-32m单线箱梁-U01已改"),
                    r("$.data.beamLength", "in", [32.2, "32.2"]),
                    r("$.data.barrierType", "eq", "0"),
                    r("$.data.lineType", "eq", "1"),
                    r("$.data.zpType", "eq", "2"),
                    r("$.data.planTotal", "in", [88, "88"]),
                    r("$.data.beamTypeColor", "eq", "#CD5C5C"),
                    r("$.data.sjth", "eq_req_body_jsonpath", "$.sjth")],
                   "回查的 sjth 应与编辑报文中的 sjth（通图号 bddId）完全一致；本次报文未改动 sjth，因此也应与新增时使用的通图号相同")],
     seeds=[("beamtype.by_name.u01", "beamtype.add.u01", True)])

case("beamtype.update.sjth", SUB_UPD, "修改梁型关联的通图号sjth生效",
     "TC-BT-551: 前置确保源数据 U02 存在并取回 btId（没有才新增）后把 sjth 由第一条通图号改为第二条通图号（${sjthB}），"
     "按 btId 回查确认 sjth 已切换且与编辑报文一致",
     [S("beamtype.update.u02", "POST 编辑 U02，sjth=${sjthB}", OK),
      verify_by_id("beamtype.update.u02.verify",
                   [r("$.data.name", "eq", "测试梁型-24m单线T梁-U02"),
                    r("$.data.sjth", "eq_req_body_jsonpath", "$.sjth")],
                   "回查的 sjth 应与编辑报文传入的 sjth 完全一致（第二条通图号的 bddId），说明已从新增时的第一条切换为第二条")],
     seeds=[("beamtype.by_name.u02", "beamtype.add.u02", True)])

case("beamtype.update.beam_location", SUB_UPD, "T型梁位置由中梁改为边梁生效",
     "TC-BT-552: 前置确保 T 梁源数据 U03 存在并取回 btId（没有才新增；20m 双线 / 中梁，beamLocation=1）后改为 2（边梁），"
     "按 btId 回查确认落库",
     [S("beamtype.update.u03", "POST 编辑 U03，beamLocation=2", OK),
      verify_by_id("beamtype.update.u03.verify",
                   [r("$.data.beamLocation", "eq", "2"),
                    r("$.data.beamBodyType", "eq", "1")])],
     seeds=[("beamtype.by_name.u03", "beamtype.add.u03", True)])

case("beamtype.update.miss_name", SUB_UPD, "缺少必填字段name修改失败且数据未变更",
     "TC-BT-553: 前置确保源数据 U04 存在并取回 btId（没有才新增）后，btId 正确但不传 name，必填校验应拦截；"
     "按 btId 回查确认原值未被改动",
     [S("beamtype.update.u04.miss_name", "POST 编辑，body 无 name", FAIL(MISS)),
      verify_by_id("beamtype.update.u04.verify",
                   [r("$.data.name", "eq", "测试梁型-32m单线箱梁-U04")],
                   desc="GET 通过id回查，确认名称未被改动")],
     seeds=[("beamtype.by_name.u04", "beamtype.add.u04", True)])

case("beamtype.update.not_exist", SUB_UPD, "btId不存在时编辑返回业务提示而非异常",
     "TC-BT-555: btId=not_exist_bt_id_99999、其余字段合法，校验接口不抛异常（按已有系统行为，可能返回成功或“数据不存在”提示）",
     [S("beamtype.update.not_exist", "POST 编辑，btId 不存在",
        A([r("$.code", "eq", "200")],
          "应给出“数据不存在”类业务提示或按幂等方式处理（status 允许 0 或 1），但不得返回 500 / 数据库异常，也不得意外新增数据"))])

case("beamtype.update.no_dept", SUB_UPD, "缺少Sys-dept-id修改被拒绝且数据未变更",
     "TC-BT-556: 前置确保源数据 U06 存在并取回 btId（没有才新增）后，用只带 Authorization 的请求头改名，应被拒绝；"
     "用正常请求头按 btId 回查确认名称未变",
     [S("beamtype.update.u06.no_dept", "POST 编辑，请求头仅 Authorization，名称改为「测试梁型-越权修改-U06」",
        FAIL("缺少 Sys-dept-id 时应拒绝执行，提示缺少部门标识 / 未授权 / 无权限类信息")),
      verify_by_id("beamtype.update.u06.verify",
                   [r("$.data.name", "eq", "测试梁型-32m单线箱梁-U06")],
                   desc="GET 通过id回查，确认名称未被改成越权修改的值")],
     seeds=[("beamtype.by_name.u06", "beamtype.add.u06", True)])

case("beamtype.update.no_auth", SUB_UPD, "缺少Authorization修改被拒绝且数据未变更",
     "TC-BT-557: 前置确保源数据 U07 存在并取回 btId（没有才新增）后，用只带 Sys-dept-id 的请求头改名，应鉴权失败；回查确认名称未变",
     [S("beamtype.update.u07.no_auth", "POST 编辑，请求头仅 Sys-dept-id", NO_AUTH()),
      verify_by_id("beamtype.update.u07.verify",
                   [r("$.data.name", "eq", "测试梁型-24m双线箱梁-U07")],
                   desc="GET 通过id回查，确认名称未被改成无令牌修改的值")],
     seeds=[("beamtype.by_name.u07", "beamtype.add.u07", True)])

# ---- 通过id删除
case("beamtype.delete.by_id_success", SUB_DEL, "按btId删除梁型成功且列表不再返回",
     "TC-BT-560: 前置确保源数据 D01 存在并取回 btId（没有才新增），按 id 删除后按名称回查应为空数组",
     [S("beamtype.delete.d01", "GET 删除 btId=${btIdD01}", OK),
      S("beamtype.by_name.d01", "GET 列表查询 name=D01，确认已删除",
        OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.by_name.d01", "beamtype.add.d01", True)])

case("beamtype.delete.not_exist", SUB_DEL, "删除不存在的btId返回成功（幂等）",
     "TC-BT-561: btId=not_exist_bt_id_99999，系统已确认删除不存在的主键返回成功，校验 status=1、code=200，不返回 500 或数据库异常",
     [S("beamtype.delete.not_exist", "GET 删除，btId 不存在",
        OKX([], "删除不存在的主键应按幂等返回成功（status=1、code=200），不得返回 500 或数据库异常"))])

case("beamtype.delete.miss_param", SUB_DEL, "缺少必填参数btId删除失败",
     "TC-BT-562: 不传 btId，必填校验应拦截", [S("beamtype.delete.miss_param", "GET 删除，不传 btId", FAIL(MISS))])

case("beamtype.delete.no_auth", SUB_DEL, "缺少Authorization删除被拒绝且记录未被删除",
     "TC-BT-563: 前置确保源数据 D02 存在并取回 btId（没有才新增）后，用只带 Sys-dept-id 的请求头删除，应鉴权失败；"
     "回查确认记录仍存在（该记录由模块清场用例删除）",
     [S("beamtype.delete.d02.no_auth", "GET 删除，请求头仅 Sys-dept-id", NO_AUTH()),
      S("beamtype.by_name.d02", "GET 列表查询 name=D02，确认仍存在",
        OKX([r("$.data", "length_gt", 0), r("$.data[0].name", "eq", "测试梁型-24m单线T梁-D02")]))],
     seeds=[("beamtype.by_name.d02", "beamtype.add.d02", True)])

case("beamtype.delete.repeat", SUB_DEL, "同一btId连续删除两次的幂等性",
     "TC-BT-564: 前置确保源数据 D03 存在并取回 btId（没有才新增）后连续两次按同一 btId 删除，两次都应返回成功（第 2 次为幂等删除）；"
     "回查确认记录已不存在",
     [S("beamtype.delete.d03.first", "GET 首次删除 D03", OK),
      S("beamtype.delete.d03.second", "GET 对同一 btId 重复删除",
        OKX([], "重复删除已不存在的 btId 应按幂等返回成功（status=1、code=200），不得返回 500 或数据库异常")),
      S("beamtype.by_name.d03", "GET 列表查询 name=D03，确认已删除",
        OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.by_name.d03", "beamtype.add.d03", True)])

# ---- 批量删除
case("beamtype.delete.batch_success", SUB_BATCH, "批量删除多个btId全部生效",
     "TC-BT-570: 前置确保 2 条源数据 B01/B02 存在并取回 btId（各自没有才新增），btIds 用英文逗号拼接后批量删除，逐条回查均已不存在",
     [S("beamtype.delete.batch.b01_b02", "GET 批量删除 btIds=${btIdB01},${btIdB02}", OK),
      S("beamtype.by_name.b01", "GET 列表查询 name=B01，确认已删除", OKX([r("$.data", "is_empty")])),
      S("beamtype.by_name.b02", "GET 列表查询 name=B02，确认已删除", OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.by_name.b01", "beamtype.add.b01", True),
            ("beamtype.by_name.b02", "beamtype.add.b02", True)])

case("beamtype.delete.batch_miss_param", SUB_BATCH, "批量删除缺少btIds失败",
     "TC-BT-571: 不传 btIds，必填校验应拦截",
     [S("beamtype.delete.batch.miss_param", "GET 批量删除，不传 btIds", FAIL(MISS))])

case("beamtype.delete.batch_mixed", SUB_BATCH, "批量删除含无效btId时整体成功且有效ID被删除",
     "TC-BT-572: 前置确保源数据 B03 存在并取回 btId（没有才新增）后，btIds=有效ID,not_exist_bt_id_99999，"
     "系统已确认无效ID按成功处理，校验整体返回成功，并回查确认有效ID B03 已被删除",
     [S("beamtype.delete.batch.mixed", "GET 批量删除 btIds=有效ID + 无效ID",
        OKX([], "含无效ID时接口应整体返回成功（status=1、code=200），不得返回 500 / 数据库异常")),
      S("beamtype.by_name.b03", "GET 列表查询 name=B03，确认有效ID已被删除",
        OKX([r("$.data", "is_empty")]))],
     seeds=[("beamtype.by_name.b03", "beamtype.add.b03", True)])

case("beamtype.delete.batch_no_auth", SUB_BATCH, "缺少Authorization批量删除被拒绝且记录未被删除",
     "TC-BT-573: 前置确保 2 条源数据 B04/B05 存在并取回 btId（各自没有才新增）后无鉴权批量删除，应鉴权失败；"
     "逐条回查确认记录仍在。本条为模块最后一条用例，后置步骤执行模块清场：扫描本梁场全部梁型，"
     "对「正常造数 + 本应失败但可能被放行的负向报文数据（缺梁位-A10、组合重复-A14 等）」逐个判断「存在才删」，"
     "确保不留下任何测试数据",
     [S("beamtype.delete.batch.b04_b05.no_auth", "GET 批量删除，请求头仅 Sys-dept-id", NO_AUTH()),
      S("beamtype.by_name.b04", "GET 列表查询 name=B04，确认仍存在", OKX([r("$.data", "length_gt", 0)])),
      S("beamtype.by_name.b05", "GET 列表查询 name=B05，确认仍存在", OKX([r("$.data", "length_gt", 0)]))],
     seeds=[("beamtype.by_name.b04", "beamtype.add.b04", True),
            ("beamtype.by_name.b05", "beamtype.add.b05", True)])


# ---- 基础数据生成（数据准备用例，不是功能校验用例）
# 用途：一次性把正交组合出来的 16 条梁型基础数据补进系统，供后续手工测试 / 其它测试直接使用。
# 自成一条用例、独立子模块，与功能用例不共用任何造数：自己的名称前缀（基础梁型-）、自己的通图号（sjthK）、
# 自己的图例颜色，也不进模块清场。因为「数据已经在库里」是常态，造数走前置的「先查后建」，
# 重复执行不会因判重失败；测试步骤只做一次汇总校验（按名称前缀查一遍，确认 16 条都在）。
BASE_N = len(BASE_ROWS)
BASE_DESC = (
    "TC-BT-600（**数据生成用例，不是功能校验用例**）：按正交组合生成 {n} 条梁型基础数据——"
    "梁体类型(T梁/箱梁) × 跨度(20m/24m/32m/40.375m) × 声屏障(有声/无声) 取全因子，"
    "正线类型(单线/双线)、直曲类别(直线/曲线)、T梁位置(中梁/边梁/次边梁)、计划数量(24/48/96 榀) 配平分配，"
    "任意两个因子的水平组合都至少出现一次。"
    "名称统一以 `基础梁型-` 开头，可直接从名称读出 类型/跨度/线别/声屏障/直曲/T梁位置，末位 B01~B{n:02d} 为序号。"
    "通图号统一取第 11 条（${{sjthK}}），与功能用例造数使用的 sjthA~sjthJ 不重叠；图例颜色也全部是未被占用的色值"
    "（颜色全梁场唯一），因此不会与任何功能用例造数撞判重或撞色。"
    "这批数据**不参与模块清场**，执行完长期保留；造数在本用例前置里「先查后建」（按 名称+梁体类型+长度类型 探针判断），"
    "库里已有就跳过，重复执行安全。测试步骤只做一次汇总校验"
).format(n=BASE_N)
case("beamtype.base.seed", SUB_BASE, "生成梁型基础数据（正交组合 %d 条，供手工测试使用）" % BASE_N,
     BASE_DESC,
     [S("beamtype.base.verify",
        "GET 列表查询 name=基础梁型-（前缀模糊匹配），逐条确认 %d 条基础数据均已存在" % BASE_N,
        OKX([r("$.data", "type", "list"),
             r("$.data", "length_gt", BASE_N - 1)] +
            [r("$..[?(@.name=='%s')].btId" % _x["name"], "not_empty") for _x in BASE_ROWS],
            "%d 条基础数据应全部存在（名称含类型/跨度/线别/声屏障/直曲/T梁位置，末位 B01~B%02d）；"
            "缺任意一条说明前置的新增步骤没有真正落库（可查该条的新增请求返回）" % (BASE_N, BASE_N)))],
     pre=PRE(min_sjth=10),
     seeds=[("beamtype.base.probe." + _x["code"], "beamtype.base.add." + _x["code"]) for _x in BASE_ROWS])


# ---------------------------------------------------------------- 3. 模块清场
# 清场名单从「所有新增/编辑报文」自动收集，不再人工维护（原先手写清单漏过 缺梁位-A10 这类负向名称）：
#   ① 本应成功落库的数据（正常造数）；
#   ② 本应被拒绝、但万一系统放行就会留下脏数据的负向报文（缺通图号-A07、缺计划-A08、缺颜色-A09、缺梁位-A10、
#      组合重复-A14、颜色重复-A15、未授权-A11……）。这类数据「本不该存在」，一旦落库同样是遗留数据，
#      必须和正常造数一样在后置清场里判断「存在才删」。
# 同一名称可能对应多条记录（同名用例 A17 两条），按出现顺序取第 n 个 btId 分别删除。
CLEAN_PREFIX = "测试梁型-"
_clean = []            # [(suffix, name, index)]
_name_count = {}
for _d in test_data:
    if _d["api_info_id"] not in (API["add"], API["update"]):
        continue
    _b = _d.get("data")
    if not isinstance(_b, dict):
        continue
    _nm = _b.get("name")
    if not isinstance(_nm, str) or not _nm.startswith(CLEAN_PREFIX):
        continue
    _idx = _name_count.get(_nm, 0)
    if _d["api_info_id"] == API["update"] and _idx > 0:
        continue        # 编辑不产生新记录：同名已在名单里就不必重复生成清场项
    _name_count[_nm] = _idx + 1
    _suffix = re.sub(r"[^A-Za-z0-9]", "", _d["key"].split(".", 2)[2]).upper()
    if _d["api_info_id"] == API["update"]:
        _suffix = "UPD" + _suffix      # 编辑数据与同名的新增数据区分开，避免清场键冲突
    _clean.append((_suffix, _nm, _idx))

# 「缺 name」的负向报文若被放行，记录没有名称可定位，改用该条报文独有的图例颜色定位。
# 只处理**真的没有 name 字段**的报文：基础数据（基础梁型-*）有名称、且要长期保留，绝不能按颜色兜底删掉。
_color_clean = []
for _d in test_data:
    _b = _d.get("data")
    if _d["api_info_id"] != API["add"] or not isinstance(_b, dict):
        continue
    if "name" in _b:
        continue
    if isinstance(_b.get("beamTypeColor"), str):
        _color_clean.append((re.sub(r"[^A-Za-z0-9]", "", _d["key"].split(".", 2)[2]).upper(),
                             _b["beamTypeColor"]))

scan_extract = []
for _suffix, _nm, _idx in _clean:
    scan_extract.append(ex("finBtId" + _suffix, "$..[?(@.name=='%s')].btId" % _nm,
                           "清场用：按名称定位「%s」的 btId%s" % (_nm, "" if _idx == 0 else "（同名第 %d 条）" % (_idx + 1)),
                           _idx))
for _suffix, _color in _color_clean:
    scan_extract.append(ex("finColor" + _suffix, "$..[?(@.beamTypeColor=='%s')].btId" % _color,
                           "清场用：无名称报文（%s）按独有的图例颜色 %s 定位" % (_suffix, _color)))

td("beamtype.cleanup.scan_all", "清场扫描-本梁场全部梁型",
   "不带过滤条件查询本梁场全部梁型，按 %d 个测试梁型名称逐一提取 btId" % len(_clean)
   + "（含负向报文名称与同名第 2 条）" + ("，另按 %d 个无名称报文的图例颜色提取" % len(_color_clean) if _color_clean else ""),
   API["list"], H_OK, None, None, scan_extract)

for _suffix, _nm, _idx in _clean:
    td("beamtype.cleanup.del_" + _suffix, "清场删除-%s" % _nm,
       "按 btId 删除「%s」（扫描到才执行，幂等）" % _nm, API["del"], H_OK, None,
       {"btId": "${finBtId%s}" % _suffix}, None)
for _suffix, _color in _color_clean:
    td("beamtype.cleanup.del_color_" + _suffix, "清场删除-无名称报文（%s）" % _color,
       "按扫描到的 btId 删除图例颜色为 %s 的无名称记录（扫描到才执行，幂等）" % _color,
       API["del"], H_OK, None, {"btId": "${finColor%s}" % _suffix}, None)

cleanup_items = []
for _suffix, _nm, _idx in _clean:
    # 第 1 条：存在即删；第 n 条（同名）：至少 n+1 条记录才删，避免取不到下标
    _rule = (r("$..[?(@.name=='%s')].btId" % _nm, "not_empty") if _idx == 0
             else r("$..[?(@.name=='%s')].btId" % _nm, "length_gt", _idx))
    cleanup_items.append({
        "assertion_config": A([_rule]),
        "steps_after_failure": [],
        "steps_after_success": ["beamtype.cleanup.del_" + _suffix],
    })
for _suffix, _color in _color_clean:
    cleanup_items.append({
        "assertion_config": A([r("$..[?(@.beamTypeColor=='%s')].btId" % _color, "not_empty")]),
        "steps_after_failure": [],
        "steps_after_success": ["beamtype.cleanup.del_color_" + _suffix],
    })

# 清场不作为独立用例，改为挂在承载清场的用例（batch_no_auth）的后置步骤中
# （按 key 定位而不是取 cases[-1]：基础数据生成用例在 JSON 里排在它后面，但 order=0 会先执行）
_cleanup_post = [{"api_res_exist": [{"test_data_key": "beamtype.cleanup.scan_all",
                                     "judgment_criteria_items": cleanup_items}]}]
_cln_carrier = next(c for c in cases if c["key"] == "beamtype.delete.batch_no_auth")
_cln_carrier["post_steps"] = _cleanup_post
# 承载终局清场的用例在**执行顺序**上排最后：order = 模块内其余用例最大 order + 1
_cln_carrier["order"] = max(c["order"] for c in cases if c["key"] != _cln_carrier["key"]) + 1


payload = {
    "meta": {
        "module_name": MODULE,
        "project_name": PROJECT,
        "generated_from": ["梁体类型接口文档.md", "梁体与通图号.md", "基本信息接口文档.md"],
        "saved_to_db": True,
        "db_path": "D:/code/UiApiMcpTestAgent/test_data.db",
        "db_sync": "按 key upsert（更新已有、新增缺失），并清理本模块已废弃的 key，可重复执行",
        "record_count": {"api_info": len(api_info), "api_test_data": len(test_data), "api_test_case": len(cases)},
        "base_data": {"case_key": "beamtype.base.seed", "prefix": BASE_PREFIX, "count": len(BASE_ROWS),
                      "sjth_var": "sjthK", "cleaned_by_module_cleanup": False,
                      "design": "梁体类型(2)×跨度(4)×声屏障(2) 全因子正交 + 正线类型/直曲类别/T梁位置/计划数量 配平，任意两因子水平组合至少出现一次"},
        "note": "按评审反馈更新：分页参数改 pageSize；name 为模糊匹配（新增模糊匹配用例）；前置增加 bfmBeamField 存在性检查；删除不存在/无效主键按返回成功断言；sjth 校验：请求报文在测试步骤内时用 eq_req_body_jsonpath，只读用例（造数已前置）改用上下文变量做期望值（AssertionRule.ctx.is_ctx_var=True，expect_value 填键名、不带 ${}，执行时自动替换）；已移除「梁体类型改为非法枚举值」编辑用例与新增接口的两条非法枚举用例；order 字段按规则取值（普通用例 0，承载终局清场的用例为模块内最大 order+1）；新增基础数据生成用例 beamtype.base.seed：正交组合 16 条 基础梁型-*，通图号独占 sjthK，不参与模块清场",
    },
    "api_info": api_info,
    "api_test_data": test_data,
    "api_test_case": cases,
}

# ---------------------------------------------------------------- 4. 自检
# 本模块直接复用数据库中已有的基础数据（不重复造），这些 key 不在本文件的 test_data 里
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
api_ids = {x["id"] for x in api_info}
problems = []
for d in test_data:
    if d["api_info_id"] not in api_ids:
        problems.append("test_data %s 引用了不存在的 api_info_id %s" % (d["key"], d["api_info_id"]))
for c in cases:
    refs = [s["test_data_key"] for s in (c["test_steps"] or [])]
    for p in (c["pre_requisites"] or []):
        for block in p.get("api_res_exist", []) or []:
            refs.append(block["test_data_key"])
    for p in (c["post_steps"] or []):
        for block in p.get("api_res_exist", []) or []:
            refs.append(block["test_data_key"])
        for block in p.get("api_res_not_exist", []) or []:
            refs.append(block["test_data_key"])
    for ref in refs:
        if ref not in td_keys:
            problems.append("case %s 引用了不存在的 test_data: %s" % (c["key"], ref))
    # 检查 steps_after_failure / steps_after_success 引用
    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("steps_after_failure", "steps_after_success"):
                    for kk in v:
                        if kk not in td_keys:
                            problems.append("case %s 的 %s 引用了不存在的 test_data: %s" % (c["key"], k, kk))
                else:
                    walk(v)
        elif isinstance(node, list):
            for i in node:
                walk(i)
    walk(c["pre_requisites"])
    walk(c["post_steps"])

# ---- 判重七项要素与图例颜色：按「执行过程中真实同时存在的落库状态」做全量校验
# 系统规则：梁体类型 + 长度类型 + 通图号 + 正线类型 + 声屏障 + T梁位置 + 直曲类别 全同即判重；
#          架设图例颜色全梁场唯一（跨梁体类型也不能重复）。
# 做法：不再手工维护「落地数据清单」（以前靠人工同步，后来补 A12 时漏登记，就和 A01 撞了组合+颜色），
# 直接从用例里挑出断言 status=1 的新增/编辑步骤：
#   · 新增成功 → 记录落地；编辑成功 → 按原地替换处理（编辑后旧状态消失，新状态参与校验）；
#   · 负向报文（断言 status=0 / 仅 AI 断言）不落库，但仍要求不与任何落地状态撞车，
#     否则系统可能先返回「梁型重复 / 颜色重复」，负向用例断言的提示语就落空了。
TD_BY_KEY = {d["key"]: d for d in test_data}
_live = {}        # 归属键 -> (组合, 颜色, 名称, 数据 key)
_neg_states = []  # (数据 key, 组合, 颜色, 自身归属键)
_executed = {}    # 新增/编辑数据 -> 执行它的用例

# 判重用例本身就是要撞车的：这两条负向报文刻意与基线完全相同（断言「新增被拒绝」）
INTENDED = {
    ("beamtype.add.a05.dup", "beamtype.add.a05.seed"),          # 七项要素完全相同的组合重复
    ("beamtype.add.a15.dup_color", "beamtype.add.a16.seed"),    # 图例颜色完全相同（跨梁体类型）
}


def _combo_of(b):
    return (b.get("beamBodyType"), b.get("beamLengthType"), b.get("sjth"), b.get("lineType"),
            b.get("barrierType"), b.get("beamLocation") or "", b.get("zpType"))


def _is_success(step):
    for _r in (step.get("assertion_config") or {}).get("assertion_rules") or []:
        _ev = _r.get("expect_value")
        if isinstance(_ev, dict) and str(_ev.get("status")) == "1":
            return True
    return False


for _c in cases:
    for _s in _c["test_steps"] or []:
        _k = _s.get("test_data_key")
        if not _k or _k not in TD_BY_KEY:
            continue
        if TD_BY_KEY[_k]["api_info_id"] not in (13, 14):
            continue
        _executed.setdefault(_k, []).append(_c["key"])
        _b = TD_BY_KEY[_k].get("data") or {}
        _parts = _k.split(".")
        _own = ("beamtype.add." + _parts[2]) if len(_parts) > 2 else _k
        if _own not in TD_BY_KEY:
            _own = _k
        if _is_success(_s):
            _live[_own] = (_combo_of(_b), _b.get("beamTypeColor"), _b.get("name"), _k)
        else:
            _neg_states.append((_k, _combo_of(_b), _b.get("beamTypeColor"), _own))

# 前置里「先查后建」的造数：用例执行前会确保它存在（不存在才新增），因此同样属于落地状态。
# 但它不参与下面「被多条用例执行」的检查——多条用例共用同一条前置造数是安全的（第二条查到已存在就跳过新增）。
_PRE_SEEDS = []
for _c in cases:
    for _blk in _c["pre_requisites"] or []:
        for _item in (_blk.get("api_res_not_exist") or []):
            for _jc in _item.get("judgment_criteria_items") or []:
                for _sk in _jc.get("steps_after_success") or []:
                    if _sk.startswith(("beamtype.add.", "beamtype.base.add.")):
                        _PRE_SEEDS.append((_c["key"], _sk))

# 前置引用的测试数据必须都存在（写错 key 会导致前置静默不生效，很难定位）
for _c in cases:
    _pre_keys = []
    for _blk in _c["pre_requisites"] or []:
        for _kind in ("api_res_exist", "api_res_not_exist"):
            for _item in (_blk.get(_kind) or []):
                _pre_keys.append(_item.get("test_data_key"))
                for _jc in _item.get("judgment_criteria_items") or []:
                    _pre_keys += _jc.get("steps_after_success") or []
                    _pre_keys += _jc.get("steps_after_failure") or []
    for _pk in _pre_keys:
        # 只校验本模块自己的数据键；login./dept./beamfield. 等基础数据在其它模块维护，不在本 JSON 里
        if _pk and _pk.startswith("beamtype.") and _pk not in TD_BY_KEY:
            problems.append("前置引用了不存在的测试数据：%s（用例 %s）" % (_pk, _c["key"]))

for _c_key, _sk in _PRE_SEEDS:
    _b = TD_BY_KEY[_sk].get("data") or {}
    _live[_sk] = (_combo_of(_b), _b.get("beamTypeColor"), _b.get("name"), _sk)

# 1) 同一份新增/编辑数据只能被一条用例执行（两条用例共用一条新增数据，第二次必然被判重拒绝）
for _k, _users in _executed.items():
    if len(_users) > 1:
        problems.append("新增/编辑数据被多条用例重复执行（第二次必然判重）：%s -> %s" % (_k, _users))

# 2) 同时存在的落库状态之间，七项要素与图例颜色都不能重复
_combo_owner, _color_owner = {}, {}
for _own, (_cmb, _color, _name, _k) in _live.items():
    if _cmb in _combo_owner:
        problems.append("判重七项要素重复：%s 与 %s 完全相同 %s" % (_k, _combo_owner[_cmb], _cmb))
    _combo_owner[_cmb] = _k
    if _color:
        if _color in _color_owner:
            problems.append("图例颜色重复：%s 与 %s 都是 %s" % (_k, _color_owner[_color], _color))
        _color_owner[_color] = _k

# 3) 负向报文不能与落地状态撞组合或撞颜色（自身记录除外；判重用例的刻意重复除外）
for _k, _cmb, _color, _own in _neg_states:
    for _own2, (_cmb2, _color2, _name2, _k2) in _live.items():
        if _own2 == _own or (_k, _k2) in INTENDED:
            continue
        if _cmb == _cmb2:
            problems.append("负向数据与落地数据判重七项要素冲突：%s 与 %s 都是 %s" % (_k, _k2, _cmb))
        if _color and _color == _color2:
            problems.append("负向数据与落地数据图例颜色冲突：%s 与 %s 都是 %s" % (_k, _k2, _color))

# ---- 未被任何用例引用的数据检查（引用可能写在 test_data_key，也可能写在 steps_after_success 列表里）
_ref_keys = set()


def _collect_refs(node):
    if isinstance(node, dict):
        if "test_data_key" in node:
            _ref_keys.add(node["test_data_key"])
        for _v in node.values():
            _collect_refs(_v)
    elif isinstance(node, list):
        for _i in node:
            _collect_refs(_i)
    elif isinstance(node, str) and node.startswith("beamtype."):
        _ref_keys.add(node)


for _c in cases:
    for _f in ("pre_requisites", "test_steps", "post_steps"):
        _collect_refs(_c.get(_f))
for _d in test_data:
    if _d["key"] not in _ref_keys:
        problems.append("测试数据未被任何用例引用：%s" % _d["key"])

# ---- 同一请求只保留一条测试数据（api + 请求头 + 请求体 + 查询参数 全同即视为重复）
# 白名单：请求相同但用途/提取不同，或本身就是「同一请求连发两次」的幂等性用例
DUP_OK = [
    {"beamtype.query.list.all", "beamtype.cleanup.scan_all"},      # 前者断言字段完整性，后者提取 41 个 btId 供清场
    {"beamtype.delete.d03.first", "beamtype.delete.d03.second"},   # 重复删除的幂等性用例本身要求同一请求发两次
]
_seen_sig = {}
for _d in test_data:
    _sig = (_d["api_info_id"],
            json.dumps(_d.get("headers"), sort_keys=True, ensure_ascii=False),
            json.dumps(_d.get("data"), sort_keys=True, ensure_ascii=False),
            json.dumps(_d.get("params"), sort_keys=True, ensure_ascii=False))
    if _sig in _seen_sig:
        _prev, _cur = _seen_sig[_sig], _d["key"]
        if not any({_prev, _cur} == x for x in DUP_OK):
            problems.append("测试数据请求完全重复：%s 与 %s" % (_prev, _cur))
    else:
        _seen_sig[_sig] = _d["key"]

# ---- 通图号使用：提取的 sjthA~sjthJ 必须全部被用到；专属通图号只能被指定的那条数据使用
# （「按通图号查询」按「该通图号下只有 1 条记录」做 length_eq 1 的精确断言，独占是前提）
EXCLUSIVE_SJTH = {"${sjthC}": "beamtype.add.q03"}
_sjth_users = {}
for _d in test_data:
    _b = _d.get("data")
    if isinstance(_b, dict) and isinstance(_b.get("sjth"), str) and _b["sjth"].startswith("${sjth"):
        _sjth_users.setdefault(_b["sjth"], []).append(_d["key"])
for _v in "ABCDEFGHIJK":
    if "${sjth%s}" % _v not in _sjth_users:
        problems.append("通图号变量 sjth%s 已提取但没有任何测试数据使用" % _v)
for _var, _only in EXCLUSIVE_SJTH.items():
    _users = _sjth_users.get(_var, [])
    if _users != [_only]:
        problems.append("专属通图号 %s 应只被 %s 使用，实际：%s" % (_var, _only, _users))

# ---- 必填语义：beamTypeColor 必填；beamLocation 条件必填（T 梁必填、箱梁不传）
for _c in ADDS:
    if not _c[12]:
        problems.append("新增成功数据缺必填的 beamTypeColor：%s" % _c[0])
    if _c[3] == "1" and not _c[10]:
        problems.append("T 梁缺条件必填的 beamLocation：%s" % _c[0])
    if _c[3] == "2" and _c[10]:
        problems.append("箱梁不应传 beamLocation：%s" % _c[0])

# ---- 上下文变量断言 / eq_req_body_jsonpath 的取值可行性
# 执行器实现（assertion_base_operate._op_eq_req_body_jsonpath）：遍历本用例已执行步骤的响应，取**最后一个带请求体**的请求
# 再做 jsonpath。造数移到前置后，若测试步骤里只剩 GET，就没有请求体可比对，断言会拿 None 去比 → 必然失败。
# 这类只读用例应改用上下文变量做期望值：expect_value 填键名（不带 ${}）+ ctx.is_ctx_var=True
# （assertion_engine.run_one 派发前会替换成上下文里的实际值，任何操作符都适用）。
def _resolve_simple_path(data, path):
    node = data
    for seg in [x for x in path.lstrip("$").lstrip(".").split(".") if x]:
        if not isinstance(node, dict) or seg not in node:
            return False
        node = node[seg]
    return True


for _c in cases:
    _step_keys = [x["test_data_key"] for x in (_c["test_steps"] or [])]
    for _s in _c["test_steps"] or []:
        for _r in (_s.get("assertion_config") or {}).get("assertion_rules") or []:
            if _r.get("operator") != "eq_req_body_jsonpath":
                continue
            _bodies = [TD_BY_KEY[k].get("data") for k in _step_keys
                       if k in TD_BY_KEY and TD_BY_KEY[k].get("data")]
            if not _bodies:
                problems.append(
                    "用例 %s 的步骤 %s 用 eq_req_body_jsonpath，但本用例测试步骤里没有任何带请求体的请求"
                    "（造数在前置，库里已有数据时不会新增），取不到比对值；"
                    "应改为上下文变量断言（ctx.is_ctx_var=True）：%s"
                    % (_c["key"], _s["test_data_key"], _r.get("expect_value")))
            elif not _resolve_simple_path(_bodies[-1], _r.get("expect_value")):
                problems.append("用例 %s 的 eq_req_body_jsonpath 路径 %s 在最后一个请求体里不存在"
                                % (_c["key"], _r.get("expect_value")))

# 上下文变量的期望值：必须是键名（不带 ${}），且必须是本模块提取过、或被别处 ${} 引用过的变量
# （写错名字 = 执行时取不到值直接抛 ContextNotFound；带 ${} 也会取不到，因为上下文里存的键名不含 ${}）
_local_vars = {e["name"] for _d in test_data for e in (_d.get("extract") or [])}
_used_vars = set(re.findall(r"\$\{([A-Za-z0-9_]+)", json.dumps(payload, ensure_ascii=False)))
for _c in cases:
    for _s in _c["test_steps"] or []:
        for _r in (_s.get("assertion_config") or {}).get("assertion_rules") or []:
            _is_ctx = bool((_r.get("ctx") or {}).get("is_ctx_var")) or _r.get("operator") == "eq_context"
            if not _is_ctx:
                continue
            _v = str(_r.get("expect_value"))
            _where = "用例 %s 的步骤 %s" % (_c["key"], _s["test_data_key"])
            if "${" in _v:
                problems.append("%s 的上下文变量期望值不要带 ${}，直接填键名：%s" % (_where, _v))
                continue
            if _v not in _local_vars and _v not in _used_vars:
                problems.append("%s 引用了未知上下文变量：%s" % (_where, _v))

# ctx.is_ctx_var 只对字符串键名有意义：改成非字符串（如数字/字典）必然是误用
for _c in cases:
    for _s in _c["test_steps"] or []:
        for _r in (_s.get("assertion_config") or {}).get("assertion_rules") or []:
            if (_r.get("ctx") or {}).get("is_ctx_var") and not isinstance(_r.get("expect_value"), str):
                problems.append("用例 %s 的 is_ctx_var 断言，expect_value 应是上下文键名（字符串）：%r"
                                % (_c["key"], _r.get("expect_value")))

# 反向检查：expect_value 写成上下文变量名却没打 ctx.is_ctx_var 标记 → 会拿字符串当字面值比，永远不可能相等
for _c in cases:
    for _s in _c["test_steps"] or []:
        for _r in (_s.get("assertion_config") or {}).get("assertion_rules") or []:
            if (_r.get("ctx") or {}).get("is_ctx_var"):
                continue
            _v = _r.get("expect_value")
            if isinstance(_v, str) and _v in _local_vars:
                problems.append("用例 %s 的步骤 %s 期望值 %r 是上下文变量名，但没加 ctx.is_ctx_var=True（会被当字面值比对）"
                                % (_c["key"], _s["test_data_key"], _v))

# ---- 清场覆盖：每条新增/编辑报文里的测试名称都必须有对应的清场项
# 负向报文同样必须覆盖——它们「本应失败」，但万一被系统放行就会在库里留下脏数据（例如 缺梁位-A10）。
_clean_names = {n for _s, n, _i in _clean}
_color_clean_vars = {_s for _s, _c in _color_clean}
for _d in test_data:
    if _d["api_info_id"] not in (API["add"], API["update"]):
        continue
    _b = _d.get("data")
    if not isinstance(_b, dict):
        continue
    _nm = _b.get("name")
    _suffix = re.sub(r"[^A-Za-z0-9]", "", _d["key"].split(".", 2)[2]).upper()
    if isinstance(_nm, str) and _nm.startswith(CLEAN_PREFIX):
        if _nm not in _clean_names:
            problems.append("报文名称没有清场项（万一落库就成了遗留数据）：%s（%s）" % (_nm, _d["key"]))
    elif "name" not in _b and isinstance(_b.get("beamTypeColor"), str) and _d["api_info_id"] == API["add"]:
        if _suffix not in _color_clean_vars:
            problems.append("无名称报文缺少按颜色兜底的清场项：%s（%s）" % (_d["key"], _b["beamTypeColor"]))

# ---- 基础数据（正交组合）：自包含、不进清场、组合覆盖所有两两水平
_base_names = [x["name"] for x in BASE_ROWS]
if len(_base_names) != len(set(_base_names)):
    problems.append("基础数据名称有重复：%s" % [n for n in _base_names if _base_names.count(n) > 1])
if len(BASE_ROWS) != len(BASE_BODY) * len(BASE_SPAN) * len(BASE_BARRIER):
    problems.append("基础数据应为 梁体类型×跨度×声屏障 全因子 %d 条，实际 %d"
                    % (len(BASE_BODY) * len(BASE_SPAN) * len(BASE_BARRIER), len(BASE_ROWS)))
for _n in _base_names:
    if _n in _clean_names:
        problems.append("基础数据被纳入模块清场（跑完会被删掉）：%s" % _n)
for _x in BASE_ROWS:
    if not _x["name"].startswith(BASE_PREFIX):
        problems.append("基础数据名称缺少统一前缀 %s：%s" % (BASE_PREFIX, _x["name"]))
    if _x["body"] == "1" and not _x["loc"]:
        problems.append("基础数据里的 T 梁缺 beamLocation（必填）：%s" % _x["name"])
    if _x["body"] == "2" and _x["loc"]:
        problems.append("基础数据里的箱梁不应带 beamLocation：%s" % _x["name"])

# 两两组合覆盖率：正交表的正交列（梁体类型/跨度/声屏障/正线类型/直曲类别）必须任意两列水平组合全覆盖
_F_FULL = [("梁体类型", lambda x: x["body_label"]),
           ("跨度", lambda x: x["span_label"]),
           ("声屏障", lambda x: x["barrier"]),
           ("正线类型", lambda x: x["line"]),
           ("直曲类别", lambda x: x["zp"])]
_levels = {_n: sorted({_f(x) for x in BASE_ROWS}) for _n, _f in _F_FULL}
for _i in range(len(_F_FULL)):
    for _j in range(_i + 1, len(_F_FULL)):
        (_n1, _f1), (_n2, _f2) = _F_FULL[_i], _F_FULL[_j]
        _pairs = {(_f1(x), _f2(x)) for x in BASE_ROWS}
        _miss = [(a, b) for a in _levels[_n1] for b in _levels[_n2] if (a, b) not in _pairs]
        if _miss:
            problems.append("基础数据正交组合未覆盖「%s × %s」：%s" % (_n1, _n2, _miss))

# T梁位置只对 T 梁有值（8 条），与 4 个跨度 × 3 个位置的 12 种组合不可能全覆盖，
# 因此只要求：三个位置都出现，且与声屏障的 6 种组合全覆盖
if {x["loc"] for x in BASE_ROWS if x["loc"]} != set(BASE_LOC):
    problems.append("基础数据的 T 梁位置没有覆盖全部 3 个水平：%s"
                    % sorted({x["loc"] for x in BASE_ROWS if x["loc"]}))
if len({(x["barrier"], x["loc"]) for x in BASE_ROWS if x["loc"]}) != len(BASE_BARRIER) * len(BASE_LOC):
    problems.append("基础数据「声屏障 × T梁位置」组合未全覆盖")
if {x["plan"] for x in BASE_ROWS} != set(BASE_PLAN):
    problems.append("基础数据的计划数量没有覆盖全部 3 档：%s" % sorted({x["plan"] for x in BASE_ROWS}))

payload["meta"]["live_state_count"] = len(_combo_owner)

if problems:
    print("自检发现问题：")
    for p in problems:
        print(" -", p)
else:
    print("自检通过：api_info=%d, test_data=%d, test_case=%d（判重组合 %d 个、图例颜色 %d 个均无重复）"
          % (len(api_info), len(test_data), len(cases), len(_combo_owner), len(_color_owner)))

with open(os.path.join(BASE, "梁型管理-接口测试用例.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
print("已生成 梁型管理-接口测试用例.json")
