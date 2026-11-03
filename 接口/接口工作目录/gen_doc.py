# -*- coding: utf-8 -*-
"""根据生成的 JSON 输出 Markdown 说明文档"""
import json
import io
import os
import sqlite3
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(io.open(os.path.join(BASE, "梁型管理-接口测试用例.json"), encoding="utf-8"))

cases = d["api_test_case"]
tds = d["api_test_data"]

# ---- 从库里取实际 id 区间与表总量，避免文档写死数字后与实际入库结果脱节
DB_PATH = "D:/code/UiApiMcpTestAgent/test_data.db"
_con = sqlite3.connect(DB_PATH)


def _range(table, keys):
    keys = list(keys)
    ph = ",".join("?" * len(keys))
    lo, hi = _con.execute("select min(id), max(id) from %s where key in (%s)" % (table, ph), keys).fetchone()
    return lo, hi


def _total(table):
    return _con.execute("select count(*) from %s" % table).fetchone()[0]


API_RANGE = "%d~%d" % (min(a["id"] for a in d["api_info"]), max(a["id"] for a in d["api_info"]))
TD_LO, TD_HI = _range("api_test_data", [x["key"] for x in tds])
CASE_LO, CASE_HI = _range("api_test_case", [x["key"] for x in cases])
TD_RANGE = "%d~%d" % (TD_LO, TD_HI)
CASE_RANGE = "%d~%d" % (CASE_LO, CASE_HI)
TOTAL_API, TOTAL_TD, TOTAL_CASE = _total("api_info"), _total("api_test_data"), _total("api_test_case")

# 清场扫描步骤里提取的 btId 个数（= 判据数，含同名第 2 条兜底）
_scan = [x for x in tds if x["key"] == "beamtype.cleanup.scan_all"]
CLEANUP_N = len(json.loads(_scan[0]["extract"])) if isinstance(_scan[0]["extract"], str) else len(_scan[0]["extract"])
apis = d["api_info"]

# 落地记录数（判重组合/颜色口径）与基础数据条数：由生成脚本写入 meta，避免文档写死数字
LIVE_N = d["meta"].get("live_state_count", 0)
BASE_ROWS = [x for x in tds if x["key"].startswith("beamtype.base.add.")]
BASE_N = len(BASE_ROWS)
BASE_PROBE_N = len([x for x in tds if x["key"].startswith("beamtype.base.probe.")])

SUBS = OrderedDict()
for c in cases:
    SUBS.setdefault(c["sub_module_name"], []).append(c)

L = []
w = L.append

w("# 梁型管理 接口测试用例说明")
w("")
w("> 产出时间：2026-10-27　|　模块：`梁型管理`　|　项目：`组织机构管理系统`")
w("> **用例已写入数据库** `test_data.db`（`api_info` %s / `api_test_data` %s / `api_test_case` %s）。" % (API_RANGE, TD_RANGE, CASE_RANGE))
w("> 变更记录：① 移除「梁体类型改为非法枚举值」编辑用例及 5 条配套数据；② 分页参数改 `pageSize`；③ `name` 按模糊匹配补用例；④ 前置补 `bfmBeamField`；⑤ 删除类接口按「返回成功」断言；⑥ `sjth` 改用 `eq_req_body_jsonpath` 校验；⑦ 移除新增接口的两条非法枚举用例及 2 条配套数据；⑧ 终局清场不再单独成用例，改为挂在模块最后一条用例的后置步骤；⑨ 用例 id 按逻辑执行顺序重排为 418~461（后补的模糊匹配用例曾占 464 排到了最后）；⑩ 适配 `api_test_case.order` 字段（普通用例 0，承载终局清场的用例为 1）；⑪ 按系统判重规则（七项要素全同才重复、颜色不允许重复、名称无唯一校验）重排全部造数并补充判重用例；⑫ 确认架设图例颜色为**全梁场唯一**，颜色重复用例改为**跨梁体类型**取数（A16 箱梁 / A15 T梁，同色），可区分「全梁场唯一」与「同类型内唯一」；⑬ 确认 `beamTypeColor` 为必填、`beamLocation` 为条件必填（T梁必填 / 箱梁可不传），原「仅必填字段新增成功」用例补上颜色断言、新增「缺 beamTypeColor」「T梁缺 beamLocation」两条负向用例，缺参报文全部改用独立组合与独立颜色；⑭ 同步库内 `api_info.response_model`，并做请求级去重：8 条「按名称回查」重复数据合并为 `beamtype.by_name.<code>`（新增后取 btId 与删除后回查共用一条），存量 163 → 152 条测试数据（合并 8 条重复 + 清理 3 条从未被引用的孤儿数据）；⑮ 按判重规则（七项要素 + 全梁场颜色唯一）重做落库状态去重：分页「每页 1 条」改为独立造数 P03（原先与「第 2 页」共用 P02A，第二次新增必然被判重）、`A12 缺部门标识` 换独立组合与颜色（原先与 A01 完全相同）、7 条编辑报文补上必填主键 `btId`、编辑负向报文改用独立组合与颜色，并把自检改为**数据驱动**（从用例反推落地状态，不再人工维护清单）；另把 Q02 由「无声」改为「有声」，它与 A02 原先只差 T 梁位置一项，现在至少差两项，降低对后端判重实现细节的依赖。存量 152 → 154 条测试数据（新增 P03 及其清场行）；⑯ 优化通图号使用：原全部造数共用 `sjthA`，现按用途分 10 组取用系统自带的 10 条通图号（`sjthA`~`sjthJ`），Q03 独占 `sjthC`，「按通图号查询」因此可断言 `length_eq 1` + 名称 + 梁体类型，真正验证过滤生效（原先只校验首条 `sjth`，而所有记录 `sjth` 都相同，等于没验）；同时把编辑报文的 `sjth` 与各自新增基线对齐（原先 U01/U03/U04/U06/U07 编辑时 `sjth` 从 `sjthG` 被改成 `sjthA`，等于顺手换了通图号）；⑰ 查询 / 分页 / 按 id 查询 / 编辑 / 删除 / 批量删除这几类用例的造数**全部移入前置条件**，改为「先查后建」——探针按「名称 + 梁体类型 + 长度类型」查一次，查不到才新增、已存在直接复用，需要 `btId` 的再查一次取主键；新增子模块的 3 条基线（A05/A16/A17）同样移入前置。目的：库里已有同一条数据时不再重复新增（重复新增会被判重拒绝），避免因此把整条用例带失败。配套新增 13 条存在性探针 `beamtype.probe.<code>`。⑱ 造数前置化后，测试步骤里不再有新增请求报文，`eq_req_body_jsonpath` 取不到比对值：436「按通图号 sjth 过滤查询」改用上下文变量 `sjthC` 做期望值，「通过 id 查询」同样改用 `sjthF`（二者本身都是只读用例，步骤里只有 GET）；⑲ 按新版断言规则，上下文变量改用 `AssertionRule.ctx.is_ctx_var=True` 机制——`expect_value` 只填键名（不带 `${}`），由执行器在派发操作符前自动替换成上下文实际值，因此任意操作符（`eq` / `contains` / `gt` …）都能用上下文变量做期望值，不再依赖 `eq_context` 这一专用操作符。生成脚本的自检同步升级：`eq_req_body_jsonpath` 在本用例步骤里找不到带请求体的请求即报错并提示改用 `ctx.is_ctx_var`；上下文变量期望值带 `${}`、引用未知变量、或 `expect_value` 不是字符串均报错。⑳ 后置清场名单改为**数据驱动**：原先手写清单漏掉了 `缺梁位-A10`、`缺通图号-A07`、`缺计划-A08`、`缺颜色-A09` 这类「本应被拒绝」的负向报文名称——万一后端放行，这些记录就会永久留在库里。现改为从所有新增/编辑报文里自动收集 `测试梁型-` 名称（正常造数 + 负向报文），清场判据 41 → 47 条；「缺 name」的报文（A06）没有名称可定位，额外按该条报文独有的图例颜色（#1E3A8A）兜底扫描。生成脚本新增覆盖自检：任一报文名称没有清场项、或无名称报文缺少颜色兜底即报错。㉑ 新增**基础数据生成用例** `beamtype.base.seed`（独立子模块「基础数据」，数据准备用，不是功能校验用例）：按正交组合生成 %d 条 `基础梁型-*`，覆盖 T梁/箱梁 × 4 种跨度 × 有声/无声屏障 全因子，正线类型/直曲类别/T梁位置/计划数量配平，任意两因子水平组合至少出现一次；通图号独占第 11 条 `${sjthK}`、图例颜色全部取未用色值，因此与功能用例造数完全不冲突；名称前缀 `基础梁型-` 不在清场名单内，执行完长期保留供手工测试使用。" % BASE_N)
w("")
w("## 一、本次做了什么")
w("")
w("依据三份接口文档（`梁体类型接口文档.md`、`梁体与通图号.md`、`基本信息接口文档.md`），为「梁型管理」模块产出用例定义，并已按规则写入测试数据库：")
w("")
w("| 类别 | 数量 | 说明 |")
w("| --- | --- | --- |")
w("| 接口信息 api_info | %d | 梁体类型 7 个接口 + 通图号列表 1 个（用于取 sjth） |" % len(apis))
w("| 测试数据 api_test_data | %d | 请求头/请求体/查询参数/结果提取，含 %d 条存在性探针（先查后建）、%d 条清场数据、%d 条基础数据（%d 条新增 + %d 条探针 + 1 条汇总查询） |"
  % (len(tds), len([x for x in tds if x["key"].startswith("beamtype.probe.")]),
     len([x for x in tds if x["key"].startswith("beamtype.cleanup.")]), BASE_N * 2 + 1, BASE_N, BASE_PROBE_N))
w("| 测试用例 api_test_case | %d | %d 条功能用例（覆盖功能、边界、必填校验、鉴权、越权（租户隔离）、注入安全）+ 1 条基础数据生成用例（`beamtype.base.seed`，非功能校验） |" % (len(cases), len(cases) - 1))
w("")
w("产物文件：")
w("")
w("- `梁型管理-接口测试用例.json`：完整定义（api_info / api_test_data / api_test_case 三个数组）")
w("- `梁型管理-测试用例说明.md`：本文件")
w("- `gen_beamtype_cases.py`：用例定义生成脚本（改数据后重跑即可再生 JSON，内置引用完整性自检）")
w("- `insert_to_db.py`：入库脚本（写前做 id / key 冲突检查，冲突整体回滚）")
w("- `gen_doc.py`：本说明文档生成脚本")
w("")
w("## 二、接口清单")
w("")
w("| id | 子模块 | 方法 | 路径 | 响应模型 | 备注 |")
w("| --- | --- | --- | --- | --- | --- |")
notes = {
    10: "取通图号 bddId 作为梁型 sjth，只读不新增",
    11: "query 参数 `pageNum` / `pageSize`（接口实际参数，文档笔误已更正）",
    12: "8 个可选过滤条件，返回 `data` 数组",
    13: "成功不返回主键，需再查列表取 `btId`；必填 10 项（含 `beamTypeColor`），`beamLocation` 仅 T 梁必填",
    14: "按 `btId` 修改，必填项需全量回传",
    15: "返回 `data` 对象",
    16: "参数 `btId`",
    17: "参数 `btIds`，英文逗号拼接",
}
for a in apis:
    w("| %d | %s | %s | `%s` | `%s` | %s |" % (a["id"], a["sub_module_name"], a["method"], a["endpoint"],
                                           a.get("response_model") or "-", notes.get(a["id"], "")))
w("")
w("## 三、请求头规范")
w("")
w("所有梁型接口与通图号接口统一携带：")
w("")
w("```json")
w('{"Authorization": "${loginUserToken}", "Sys-dept-id": "${bfDeptId}"}')
w("```")
w("")
w("- `Authorization`：取自 `login.success` 提取的 `loginUserToken`（已带 `Bearer ` 前缀）")
w("- `Sys-dept-id`：梁场机构 deptId，取自 `beamfield.dept.verify_f01` 提取的 `bfDeptId`（该值同时用于越权/缺省头的负向用例：缺失时只带 Authorization，伪造时用 `999999999`）")
w("")
w("## 四、通图号 sjth 的取数方式")
w("")
w("梁型的 `sjth` 就是通图号管理的 `bddId`，由系统自动生成，**不新建通图号**，直接查询取用：")
w("")
w("```")
w("GET /api/base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoList.ajax")
w("```")
w("")
w("对应测试数据 `beamtype.sjth.list`，按用途分 10 组提取——系统自带 10 条以上，一条通图号下挂一组梁型，比全部挤在同一条上更接近真实数据：")
w("")
w("| 变量 | JSONPath | 使用的数据 |")
w("| --- | --- | --- |")
w("| `sjthA` | `$.data[0].bddId` | 基础新增组 A01~A05、判重/颜色/同名基线、SQL 注入数据 |")
w("| `sjthB` | `$.data[1].bddId` | 「编辑-更换通图号」的目标值（U02 由 `sjthG` 改为 `sjthB`） |")
w("| `sjthC` | `$.data[2].bddId` | **Q03 独占**，该通图号下只有 1 条梁型，供「按通图号查询」做精确断言 |")
w("| `sjthD` | `$.data[3].bddId` | 列表查询组 Q01 / Q02 / Q05 |")
w("| `sjthE` | `$.data[4].bddId` | 分页组 P01 / P02A / P02B / P03 |")
w("| `sjthF` | `$.data[5].bddId` | 通过 id 查询 G01 |")
w("| `sjthG` | `$.data[6].bddId` | 编辑组 U01~U07（U02 编辑时改为 `sjthB`） |")
w("| `sjthH` | `$.data[7].bddId` | 通过 id 删除 D01~D03 |")
w("| `sjthI` | `$.data[8].bddId` | 批量删除 B01~B05 |")
w("| `sjthJ` | `$.data[9].bddId` | 模糊匹配 F01 / F02 |")
w("| `sjthK` | `$.data[10].bddId` | **基础数据独占**（`基础梁型-*` 共 %d 条），与功能用例造数隔离，执行完不清理 |" % BASE_N)
w("| `sjthDrawingA` / `sjthBeamCodeA` | `$.data[0].designDrawingsNumber` / `designBeamType` | 核对图号与梁型码，便于人工确认取数是否正确 |")
w("")
w("前置判据是 `$.data` 长度 > 9（即至少 10 条）：数量不足时前置直接失败并给出明确提示，避免提取到空值后在用例里报出难以定位的错误。基础数据用例要取第 11 条，因此它的前置判据单独抬高为长度 > 10。")
w("")
w("`sjthC` 是「按通图号查询」能做出强断言的前提——只有该通图号下独占一条记录，才敢断言返回 `length_eq 1`；否则按通图号查到一堆记录、只校验首条，等于没验证过滤是否生效。生成脚本内置两条自检：`sjthA`~`sjthK` 必须全部被使用；`sjthC` 只能被 Q03 使用。")
w("")
w("> 编辑类报文（U01/U03/U04/U06/U07、主键不存在）的 `sjth` 与各自新增基线保持一致（`sjthG`），只有「更换通图号」用例刻意改为 `sjthB`——否则「sjth 保持不变」的全字段修改用例实际把通图号也改了。")
w("")
w("## 五、基础数据准备（复用已有的 13 个数据键）")
w("")
w("不重复造组织机构，直接复用测试数据表中已有的链路数据，并在**每条用例**的前置条件中做「存在性检查，不存在才新增」：")
w("")
w("```")
w("login.success                     → loginUserToken")
w("dept.query.tree_success           → yunweiDeptId（运维单位）")
w("beamfield.prep.detect_chain       → 查树判断梁场机构 TESTLC201 是否存在，同时提取 bfDeptId")
w("   └ 不存在时依次执行：")
w("       beamfield.prep.add_group           → 新增集团公司 G01（deptType=2）")
w("       beamfield.prep.get_group_id        → 提取 groupId")
w("       beamfield.prep.add_build_unit      → 建设单位 G02（deptType=3）")
w("       beamfield.prep.get_build_unit_id   → 提取 buildUnitId")
w("       beamfield.prep.add_proj            → 建设项目 G03（deptType=4）")
w("       beamfield.prep.get_proj_id         → 提取 projId")
w("       beamfield.prep.add_section         → 标段 G04（deptType=5）")
w("       beamfield.prep.get_section_id      → 提取 sectionId")
w("       beamfield.dept.create_f01          → 梁场 F01（deptType=6）")
w("       beamfield.dept.verify_f01          → 提取 bfDeptId")
w("beamfield.query.by_dept           → 查本梁场 bfmBeamField 记录（梁场基本信息）")
w("   └ 查不到时执行：")
w("       beamfield.prepare.add              → 以 deptId=${bfDeptId} 新增梁场基本信息")
w("```")
w("")
w("即：梁场机构与梁场基本信息都已存在时 0 次写操作；机构不存在时按 集团→建设单位→项目→标段→梁场 逐级补齐，基本信息缺失时再补一条。")
w("")
w("这两类都属于**环境初始化数据**（组织机构链路、梁场基本信息），按清场规则不做删除，模块清场只清本模块产生的梁型记录。")
w("")
w("## 六、用例清单（%d 条）" % len(cases))
w("")
for sub, items in SUBS.items():
    w("### %s（%d 条）" % (sub, len(items)))
    w("")
    w("| # | key | 用例标题 | 步骤数 |")
    w("| --- | --- | --- | --- |")
    for i, c in enumerate(items, 1):
        w("| %d | `%s` | %s | %d |" % (i, c["key"], c["title"], len(c["test_steps"])))
    w("")

w("## 七、基础数据（正交组合，供手工测试使用）")
w("")
w("模块里另有一条**独立用例** `beamtype.base.seed`（子模块「基础数据」，`TC-BT-600`），它不是功能校验用例，只负责把一批梁型基础数据补进系统，供后续手工测试 / 其它测试直接使用。")
w("")
w("**为什么单独成一条用例、且不与功能用例混用数据**：")
w("")
w("| 隔离点 | 做法 | 原因 |")
w("| --- | --- | --- |")
w("| 名称前缀 | 统一 `基础梁型-` | 模块清场只删 `测试梁型-`，这批数据执行完会长期保留；反过来也不会被误认为功能用例造数 |")
w("| 通图号 | 独占第 11 条 `${sjthK}` | 功能用例造数用 `sjthA`~`sjthJ`，两者七项判重组合天然不重叠，不会互相触发「梁型重复」 |")
w("| 图例颜色 | %d 个全新色值 | 颜色全梁场唯一，必须避开功能用例已占用的 %d 个色值，否则新增会被颜色重复校验拒绝 |" % (BASE_N, LIVE_N - BASE_N))
w("| 数据键 | `beamtype.base.*` | 与 `beamtype.add.*` / `beamtype.probe.*` / `beamtype.cleanup.*` 完全分开，便于单独维护 |")
w("| 清场 | 不参与 | 基础数据是「要留下的」，模块清场只清 `测试梁型-*`；生成脚本有自检，防它被误纳入清场 |")
w("")
w("**组合设计**：梁体类型(2) × 跨度(4) × 声屏障(2) 取**全因子正交**（2×4×2 = %d 条，每条组合恰好出现一次），"
  "正线类型 / 直曲类别 / T梁位置 / 计划数量 按正交表配平分配，**任意两个因子的水平组合都至少出现一次**"
  "（生成脚本内置覆盖率自检）。T 梁位置只对 T 梁有值（8 条），与 4 种跨度的 12 种组合不可能全覆盖，因此按「3 个位置都出现 + 与声屏障的 6 种组合全覆盖」校验。" % BASE_N)
w("")
w("| # | 名称 | 梁体类型 | 跨度 | 线别 | 声屏障 | 直曲 | T梁位置 | 计划 | 图例颜色 |")
w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
_BT = {"1": "T梁", "2": "箱梁"}
_BAR = {"0": "无声", "1": "有声"}
_LINE = {"1": "单线", "2": "双线"}
_ZP = {"1": "直线", "2": "曲线"}
_LOC = {"1": "中梁", "2": "边梁", "3": "次边梁"}
for i, x in enumerate(BASE_ROWS, 1):
    b = x["data"]
    w("| %d | `%s` | %s | %sm | %s | %s | %s | %s | %d | `%s` |" % (
        i, b["name"], _BT.get(str(b["beamBodyType"]), b["beamBodyType"]), b["beamLength"],
        _LINE.get(str(b["lineType"]), b["lineType"]), _BAR.get(str(b["barrierType"]), b["barrierType"]),
        _ZP.get(str(b["zpType"]), b["zpType"]), _LOC.get(str(b.get("beamLocation")), "-"),
        b["planTotal"], b["beamTypeColor"]))
w("")
w("**怎么跑**：直接执行这一条用例即可。前置对每条数据先做存在性探针（按「名称 + 梁体类型 + 长度类型」），**库里已有就跳过、没有才新增**，所以重复执行是安全的；"
  "测试步骤只有一次汇总校验——按名称前缀 `基础梁型-` 查一遍，逐条断言 %d 条都已存在（共 %d 条断言）。"
  "配套数据：%d 条新增报文 + %d 条存在性探针 + 1 条汇总查询。" % (BASE_N, BASE_N + 3, BASE_N, BASE_PROBE_N))
w("")

w("## 八、数据隔离与清场策略")
w("")
w("1. **造数放在前置、先查后建**：查询 / 分页 / 按 id 查询 / 编辑 / 删除 / 批量删除这几类用例，源数据都在**前置条件**里准备——先用探针（`beamtype.probe.<code>` 或 `beamtype.by_name.<code>`，按「名称 + 梁体类型 + 长度类型」定位）查一次，**查不到才新增，已存在就直接复用**；需要 `btId` 的，在探针查到后直接提取，若走了新增分支则新增后再查一次取主键（新增接口不返回主键）。这样即使库里已有同一条数据（上一轮残留、或环境本身预置），也不会因重复新增被判重拒绝而拖垮整条用例。")
w("2. **用例之间无上下文依赖**：所有造数都在本条用例的前置里完成，可从任意一条用例开始执行，也可只跑某个子模块；`test_steps` 里只留被测请求与结果回查。")
w("3. **模块级清场**：清场不单独成用例，而是挂在**模块最后一条用例**（`beamtype.delete.batch_no_auth`）的**后置步骤**中。后置步骤用一次列表查询（不带过滤条件）扫描本梁场全部梁型，逐个按名称判断是否存在，**存在才按 `btId` 删除**，共覆盖 %d 个清场判据；即使该用例自身的测试步骤失败，后置清场仍会执行。该用例的 `order` 取模块内其余用例的最大值 + 1（本模块为 1），其余用例均为默认 0，保证它在模块内最后执行。" % len([x for x in tds if ".del_" in x["key"]]))
w("4. **清场名单覆盖「本应失败」的数据**：清场名单不再手写，而是从**所有新增/编辑报文**里自动收集 `测试梁型-` 开头的名称——既有正常造数，也有本该被拒绝的负向报文（缺通图号-A07、缺计划-A08、缺颜色-A09、**缺梁位-A10**、组合重复-A14、颜色重复-A15、未授权-A11 等）。这些数据「本不该存在」，但一旦系统放行就会变成遗留脏数据，因此与正常造数同等对待：**扫到了就删**。其中「缺 name」的那条负向报文若被放行，记录没有名称可定位，改用该报文独有的图例颜色兜底扫描（每条负向报文的颜色互不相同）。生成脚本内置覆盖自检：任一报文名称没有清场项、或无名称报文缺少颜色兜底，直接报错。")
w("5. **只清自己的数据**：只删除名称以 `测试梁型-` 开头的记录（颜色兜底也只匹配负向报文专用的独有色值），不动组织机构、通图号、梁场基本信息，也不影响他人数据；删除动作幂等，重复执行无副作用。`测试梁型-` 前缀同时也保证数据可辨识：形如 `测试梁型-32m双线箱梁-A01`、`测试梁型-24m单线T梁-B02`，一眼可辨认且符合真实命名规律。")
w("6. **断言优先 JSONPath**：状态码、枚举值、数值、字段集合等确定性内容全部用普通断言；只有提示语文案、`sjth` 业务语义、越权行为等不确定项才用 AI 断言。期望值需要用运行时的上下文变量时（如通图号 `sjthC`、主键 `btId`），在 `AssertionRule` 上写 `\"ctx\": {\"is_ctx_var\": true}`、`expect_value` 只填键名（不带 `${}`），执行器会在派发操作符前自动替换成上下文实际值——因此 `eq`、`contains`、`gt` 等任意操作符都适用。本模块的「按通图号过滤」「按 id 查询」就是用这种方式与前置提取的通图号比对（`sjthC` / `sjthF`），不再依赖测试步骤里是否存在新增报文。")
w("7. **请求级去重**：同一「接口 + 请求头 + 请求体 + 查询参数」只保留一条 `api_test_data`。此前把 8 条「按名称回查」重复数据合并为统一键 `beamtype.by_name.<code>`——新增后用它提取 `btId`，删除/批量删除后用它断言记录是否已不存在（提取用 `jsonpath`，查不到记录时该库返回 `False`、提取自动跳过，不会因空结果报错）。仅两处有意保留同请求：`beamtype.query.list.all` 与 `beamtype.cleanup.scan_all`（前者断言字段完整性，后者提取 %d 个 `btId` 供清场，提取内容不同" % CLEANUP_N + "）、`beamtype.delete.d03.first` / `beamtype.delete.d03.second`（幂等性用例本身要求同一请求连发两次）。生成脚本已内置该检查，重复即报错。")
w("8. **落库状态唯一（判重/颜色）**：模块是按顺序执行的，新增成功的记录会一直留到终局清场才删除，所以「同时存在」的两条记录不能撞七项要素、也不能撞图例颜色。生成脚本改为**数据驱动**校验：从用例里挑出断言 `status=1` 的新增/编辑步骤，新增记为落地、编辑按原地替换处理（编辑后旧状态消失），负向报文只做单向冲突检查；**前置里「先查后建」的造数同样计入落地状态**（执行前会被确保存在），但不参与「同一份数据不得被两条用例执行」的检查——多条用例共用一条前置造数是安全的，第二条查到已存在就跳过新增。判重用例本身要求的「刻意重复」（A14 撞 A05 组合、A15 撞 A16 颜色）白名单放行。")
w("")
w("## 九、覆盖要点")
w("")
w("| 维度 | 覆盖内容 |")
w("| --- | --- |")
w("| 功能正向 | 新增（箱梁/T梁/仅必填/边界值）、列表 4 种过滤（名称模糊匹配/通图号/梁体类型/无参）、分页翻页、按 id 查询、编辑（全字段/通图号/梁位）、按 id 删除、批量删除 |")
w("| 必填校验 | 新增缺 name / sjth / planTotal / **beamTypeColor** / **T梁缺 beamLocation**；编辑缺 name；查询缺 btId；删除缺 btId；批量删除缺 btIds。缺参报文的其余字段刻意使用**不与任何新增成功数据重合**的七项要素与图例颜色，避免先被「梁型重复 / 颜色重复」拦截而误判 |")
w("| 条件必填 | `beamTypeColor` 恒必填；`beamLocation` 仅 T 梁必填，箱梁可不传——用「仅必填字段新增成功（箱梁不传 beamLocation）」与「T梁缺少 beamLocation 新增失败」两条用例正反夹住 |")
w("| 判重（七项要素） | 梁体类型 + 长度类型 + 通图号 + 正线类型 + 声屏障 + T梁位置 + 直曲类别 全同即重复：判定为重复时新增被拒绝并断言未落库。**全部 %d 条落地记录**（%d 条功能用例造数 + %d 条基础数据）的七项要素互不相同（含编辑后的状态） |" % (LIVE_N, LIVE_N - BASE_N, BASE_N))
w("| 图例颜色唯一（全梁场） | 架设图例颜色在全梁场范围内唯一，跨梁体类型也不能复用：重复时新增被拒绝并断言未落库。%d 条落地记录使用 %d 个互不相同的色值（基础数据的 %d 个色值也全部避开了功能用例已用的色值） |" % (LIVE_N, LIVE_N, BASE_N))
w("| 名称可重复 | 同名但七项要素与颜色均不同的梁型可正常新增，精确回查应返回 2 条 |")
w("| 边界值 | beamLength=40.375（三位小数）、planTotal=1（最小计划量）、beamLengthType=6（其他） |")
w("| 鉴权 | 缺 Authorization：新增/列表/分页/编辑/删除/批量删除全部覆盖 |")
w("| 租户隔离 | 缺 Sys-dept-id、`Sys-dept-id=999999999`：验证不串出其他梁场数据、越权修改不生效 |")
w("| 模糊匹配 | 名称前缀命中多条（F01/F02）、完整名称命中自身、无匹配返回空数组 |")
w("| 幂等/健壮性 | 同一 btId 重复删除返回成功、批量删除含无效 id 返回成功且有效 id 被删、删除不存在主键返回成功、分页参数非法（0/-1）、按 id 查询不存在 |")
w("| sjth 一致性 | 新增/编辑用 `eq_req_body_jsonpath` 与请求报文中的 `$.sjth` 直接比对；只读用例（按 id 查询、按 sjth 过滤）步骤里没有请求体，改用上下文变量（`sjthF` / `sjthC`）+ `ctx.is_ctx_var=True` 做期望值比对 |")
w("| 安全 | 名称含 SQL 注入 payload，验证不 500、库表不受影响 |")
w("")
w("## 十、入库结果")
w("")
w("已通过 `insert_to_db.py` 写入 `D:/code/UiApiMcpTestAgent/test_data.db`：")
w("")
w("| 表 | 本次写入 | id 区间 | 库内合计 |")
w("| --- | --- | --- | --- |")
w("| `api_info` | %d | %s | %d |" % (len(apis), API_RANGE, TOTAL_API))
w("| `api_test_data` | %d | %s | %d |" % (len(tds), TD_RANGE, TOTAL_TD))
w("| `api_test_case` | %d | %s | %d |" % (len(cases), CASE_RANGE, TOTAL_CASE))
w("")
w("- `headers` / `data` / `params` / `extract` / `pre_requisites` / `post_steps` / `test_steps` 均以 JSON 文本写入（`ensure_ascii=False`），中文不转义；空值写 `NULL`")
w("- `api_test_case.module_name` 统一为 `梁型管理`，`is_active=1`")
w("- `api_test_case.order`：普通用例写默认值 `0`，承载终局清场的 `beamtype.delete.batch_no_auth` 写 `1`（模块内最大 order + 1），保证模块最后执行，与库内既有取值一致")
w("- 同步方式为**按 key upsert**（已存在的更新、缺失的新增），并清理本模块已废弃的 key；本模块用例 id 同步时按 JSON 顺序重排为 %s，使 order 相同时按 id 兜底的顺序也与用例清单一致" % CASE_RANGE)
w("- 导入后已校验：无孤立 `api_info_id`（外键 0 条异常）、用例引用的测试数据键全部存在、所有 JSON 字段可正常解析")
w("")
w("## 十一、已确认的接口行为（断言依据）")
w("")
w("| # | 事项 | 已确认结论 | 用例对应的断言 |")
w("| --- | --- | --- | --- |")
w("| 1 | 分页参数 | 接口参数为 `pageSize`（`pagSize` 为文档笔误，已更正） | `beamtype.query.page.*` 统一传 `pageNum` + `pageSize` |")
w("| 2 | `name` 过滤 | 模糊匹配（包含即命中） | 新增「按名称模糊匹配」用例断言 `length > 1` 且命中项名称包含关键字；完整名称查询仍以 `data[0].name` 精确断言 |")
w("| 3 | 通图号数量 | 系统自带 10 条以上，按用途分 10 组取用 `sjthA`~`sjthJ`，实际存量足以支撑（本次使用了 10 条） | 前置判据为 `$.data` 长度 > 9；`sjthC` 为 Q03 独占，供「按通图号查询」做 `length_eq 1` 精确断言 |")
w("| 4 | 梁场基本信息 | 梁型依赖 `bfmBeamField`，无记录时需先新增 | 每条用例前置增加 `beamfield.query.by_dept` 探针，查不到则执行 `beamfield.prepare.add` |")
w("| 5 | 删除不存在的主键 | 返回成功（幂等） | `beamtype.delete.not_exist` 断言 `status=1`、`code=200` |")
w("| 6 | 批量删除含无效 id | 返回成功，有效的 id 正常删除 | `beamtype.delete.batch_mixed` 断言成功 + 回查 B03 已删除 |")
w("| 7 | `sjth` 校验 | 请求报文里带 `sjth` 时用 `eq_req_body_jsonpath` 比对；步骤里没有请求体（造数已前置的只读用例）改用上下文变量 + `ctx.is_ctx_var=True` | 新增回查（A01~A04）、编辑回查（U01 / U02）用 `eq_req_body_jsonpath`；按 id 查询改 `eq` + `ctx.is_ctx_var` = `sjthF`，按 sjth 过滤改 `eq` + `ctx.is_ctx_var` = `sjthC`（不再依赖新增报文）。「按通图号查询」另加 `length_eq 1` + 名称 + 梁体类型——该通图号由 Q03 独占，所以能证明“过滤真的生效”，而不只是“查得到东西” |")
w("| 8 | 梁型判重规则 | 梁体类型 + 长度类型 + 通图号 + 正线类型 + 声屏障 + T梁位置 + 直曲类别，**七项全同**才算重复 | `beamtype.add.dup_combo`：A14 与 A05 七项全同、名称颜色不同，断言失败 + 未落库 |")
w("| 9 | 架设图例颜色 | **全梁场唯一**：同一颜色不能被任何梁型占用，跨梁体类型也不行 | `beamtype.add.dup_color`：A16 为箱梁（#8B0000），A15 为 T 梁、七项要素全不同但颜色相同，断言失败 + 未落库（刻意跨梁体类型，可区分「全梁场唯一」与「同类型内唯一」） |")
w("| 10 | 梁型名称 | **没有**重复校验 | `beamtype.add.same_name`：同名 A17 两条，七项要素与颜色都不同，断言新增成功且按名称查到 2 条 |")
w("| 11 | `beamTypeColor` | **必填**（架设图例颜色不能缺席），同时又受全梁场唯一约束 | `beamtype.add.required_only` 回查 `beamTypeColor` 落库；`beamtype.add.miss_color`：不传该字段断言失败且未落库 |")
w("| 12 | `beamLocation` | **条件必填**：T 梁（`beamBodyType=1`）必填，箱梁（`beamBodyType=2`）可不传 | `beamtype.add.required_only`（箱梁不传）断言新增成功；`beamtype.add.miss_location_tbeam`（T梁不传）断言失败且未落库 |")
w("| 13 | 编辑报文的主键 | `btId` 为**请求体必填字段**（接口文档 Body 表明确「必须」），少了它无法定位记录 | 7 条编辑数据全部带 `btId`（3 条成功用例取 `${btIdU01~U03}`，2 条越权用例取 `${btIdU06}` / `${btIdU07}`，缺 name 用例取 `${btIdU04}`，主键不存在用例写 `not_exist_bt_id_99999`） |")
w("")
w("## 十二、仍需留意")
w("")
w("| # | 事项 | 说明 |")
w("| --- | --- | --- |")
w("| 1 | 分页参数非法（pageNum=0、pageSize=-1） | 后端会回退默认值还是返回参数校验提示尚未确认；用例只断言 `code=200` 且不 500，首次执行后可据实收紧 |")
w("| 2 | 按 id 查询 / 编辑不存在的 btId | 二者未在本次确认范围内；用例仍断言「`code=200` 且不得 500」，若实际返回成功可改为与删除一致的强断言 |")
w("| 3 | 模糊匹配下的排序 | 不同关键字可能命中多条，用例统一用 `data[0]` + 名称断言，若后端排序规则变化需同步调整 |")
w("| 4 | 真实数据占用颜色/组合 | 颜色唯一性为**全梁场唯一**，判重按七项要素。若库里已有真实梁型占用了某个颜色或七项要素组合，对应新增会被拒绝。本套造数的 %d 条落地记录（含 %d 条长期保留的基础数据）使用互不相同的组合与冷门色值，执行前仍建议确认库内无同组合/同色记录 |" % (LIVE_N, BASE_N))
w("| 5 | 校验顺序（必填 vs 判重） | 后端先校验必填还是先判重未确认。缺参用例（425~427）已改用独立组合与独立颜色，两种顺序下提示语都应是必填缺失；若实际返回「梁型重复」，说明判重先执行，需同步调整 AI 断言 |")
w("| 6 | `sjthC` 被真实数据占用 | 「按通图号查询」断言 `length_eq 1` 的前提是第 3 条通图号下只有 Q03 一条。这是**造数层面的独占**：若测试梁场已有引用该通图号的真实梁型，会返回多条导致失败。届时把提取索引换成一条未被占用的通图号（如 `$.data[n]` + 同步改 `sjthC`）即可，无需改断言 |")
w("| 7 | 探针的定位精度 | 「先查后建」按「名称 + 梁体类型 + 长度类型」判断该条造数是否已存在。若库里恰有同名、同梁体类型、同长度类型但其他要素不同的记录（非本套造数产生），探针会判为「已存在」而跳过新增，后续断言可能与预期不符。届时换一个造数名称即可；正常清场后不会出现该情况 |")
w("| 8 | 基础数据依赖第 11 条通图号 | `beamtype.base.seed` 用 `${sjthK}`（`$.data[10].bddId`）。系统若只有 10 条通图号，该用例前置会因 `$.data` 长度不足 11 而失败（其余 %d 条用例不受影响）。届时去通图号管理补一条，或把提取索引换成别的未占用通图号并同步改数据 |" % (len(cases) - 1))
w("| 9 | 基础数据与功能用例共存 | 基础数据长期留在库里，功能用例每次跑都会重建自己的 `测试梁型-*` 并清场。两边靠「通图号不同 + 颜色不同 + 七项要素不同」保证互不干扰（生成脚本有全量自检）；若手工改过某条基础数据的通图号或颜色，需重新跑一遍生成脚本自检 |")
w("")
io.open(os.path.join(BASE, "梁型管理-测试用例说明.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("已生成 梁型管理-测试用例说明.md，行数：", len(L))
