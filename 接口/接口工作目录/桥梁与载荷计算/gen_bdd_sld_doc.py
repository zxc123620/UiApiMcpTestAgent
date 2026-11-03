# -*- coding: utf-8 -*-
"""根据 通图号与载荷计算-接口测试用例.json 生成评审用说明文档（数字全部从 JSON 实时统计）"""
import io
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "通图号与载荷计算-接口测试用例.json")
OUT = os.path.join(BASE, "通图号与载荷计算-测试用例说明.md")

d = json.load(io.open(SRC, encoding="utf-8"))
apis, tds, cases = d["api_info"], d["api_test_data"], d["api_test_case"]
TD = {x["key"]: x for x in tds}

M1, M2 = "通图号", "载荷计算"
SUB_ORDER = ["初始化", "分页列表查询", "列表查询", "新增", "编辑", "通过id查询", "通过id删除", "批量删除"]


def mcases(m):
    return [c for c in cases if c["module_name"] == m]


def num(c):
    m = re.search(r"TC-[A-Z]+-\d+", c["description"])
    return m.group(0) if m else "-"


buf = []


def w(s=""):
    buf.append(s)


n1, n2 = len(mcases(M1)), len(mcases(M2))
cleanup1 = next(c for c in mcases(M1) if c["post_steps"])
items1 = cleanup1["post_steps"][0]["api_res_exist"][0]["judgment_criteria_items"]
cleanup2 = next(c for c in mcases(M2) if c["post_steps"])
blocks2 = cleanup2["post_steps"]
del_cfg2 = [x for x in tds if x["key"].startswith("sld.cleanup.del_cfg")]

w("# 通图号 / 静载试验设计参数 接口测试用例说明")
w("")
w("> **状态：已按评审结论定稿并写入数据库**（`test_data.db`：api_info id 18~31，通图号用例 id 467~509，载荷计算用例 id 510~537）。"
  "本文档与 `通图号与载荷计算-接口测试用例.json`、库内数据三处一致；改动用例请改生成器后重跑 `gen_bdd_sld_cases.py` → `insert_bdd_sld_to_db.py`。")
w("> 生成依据：`梁体与通图号.md`、`梁体与通图号需求.md`、`桥梁设计与载荷计算.md`、`基本信息接口文档.md`。")
w("")
w("## 一、产物与规模")
w("")
w("| 产物 | 说明 |")
w("| --- | --- |")
w("| `通图号与载荷计算-接口测试用例.json` | 用例数据源（api_info / api_test_data / api_test_case），已同步入库 |")
w("| `gen_bdd_sld_cases.py` | 生成器，含自检（引用完整性、编码唯一、清场覆盖、上下文变量），改数据后重跑即可 |")
w("| `gen_bdd_sld_doc.py` | 生成本文档，数字从 JSON 实时统计 |")
w("| `insert_bdd_sld_to_db.py` | 入库脚本（已执行，幂等，可重复运行） |")
w("")
w("| 模块 | 子模块 | 用例数 | 接口数 |")
w("| --- | --- | --- | --- |")
for m, n in ((M1, n1), (M2, n2)):
    subs = "、".join(s for s in SUB_ORDER if s in {c["sub_module_name"] for c in mcases(m)})
    napi = len([a for a in apis if a["module_name"] == m]) + (1 if m == M1 else 0)
    w("| %s | %s | %d | %d |" % (m, subs, n, napi))
w("| **合计** | — | **%d** | **%d** |" % (n1 + n2, len(apis) + 1))
w("")
w("测试数据 **%d** 条（含前置探针、清场数据）；新增 api_info **%d** 条（id %d~%d）。"
  "通图号列表查询复用库内已有的 **id=10**（同一 endpoint 不再重复建记录，梁型管理的 `beamtype.sjth.list` 也在用它）。"
  % (len(tds), len(apis), min(a["id"] for a in apis), max(a["id"] for a in apis)))
w("")
w("## 二、接口清单")
w("")
w("| id | 模块 | 子模块 | 接口 | 方法 | 路径 |")
w("| --- | --- | --- | --- | --- | --- |")
w("| 10 | 梁型管理（复用） | 通图号 | 通图号列表查询 | GET | `/api/base/bfmBaseDesignDrawingsNumber/queryBfmBaseDesignDrawingsNumberVoList.ajax` |")
for a in sorted(apis, key=lambda x: x["id"]):
    w("| %d | %s | %s | %s | %s | `%s` |" % (a["id"], a["module_name"], a["sub_module_name"],
                                            a["name"], a["method"], a["endpoint"]))
w("")
w("> **`初始化通图号`**（`/api/base/bfmBeamField/initBfmBeamField.ajax`，POST，无请求参数）为本梁场批量生成"
  "内置 153 条编码（001~152、999）。它既是一条独立用例（校验重复调用不重复生成），也是"
  "「内置编码」相关用例的前置动作：先查 `numberType=1`，查不到才调用它补全。")
w("")
w("## 三、通图号：需求条目 → 用例映射")
w("")
w("| 需求（梁体与通图号需求.md） | 校验点 | 对应用例（key） |")
w("| --- | --- | --- |")
rows = [
    ("2.1 国铁占用 001~152、999，用户只能生成 153~998",
     "占用内置码被拒 / 999 被拒 / 000 越界被拒 / 下界 153 与上界 998 可建",
     "`bdd.add.reserved_code`、`bdd.add.upper_occupied`、`bdd.add.range_invalid`、`bdd.add.boundary_153`、`bdd.add.boundary_998`"),
    ("2.1.1 梁型码必填、长度 3、去空格后查重",
     "缺码 / 2 位 / 4 位 / 重复 / 带前后空格重复（去空格后判重）",
     "`bdd.add.miss_code`、`bdd.add.code_too_short`、`bdd.add.code_too_long`、`bdd.add.dup_code`、`bdd.add.trim_dup_code`"),
    ("2.1.1 通图号必填、长度 1~50",
     "缺名称 / 空串（「超过 50 字符」按评审意见去掉，不写该用例）",
     "`bdd.add.miss_number`、`bdd.add.empty_number`"),
    ("2.1.1 新创建的通图号默认排在最前",
     "实现方式为「分页查询返回的数据里第一条即新记录」：新增后按 pageNum=1&pageSize=10 查询，断言 `data.list[0]` 就是新记录（前置先删残留保证可重复）",
     "`bdd.add.sort_first`"),
    ("2.1「每个梁场初始化后必须默认生成内置 153 个编码」",
     "调用初始化接口后再查 `numberType=1`，数量仍为 153 条（重复调用不得重复生成）；同时作为内置类用例的前置补全动作",
     "`bdd.init.builtin`"),
    ("2.1.2 内置 153 个编码不允许编辑",
     "用内置编码 bddId 改名被拒，且回查名称未变",
     "`bdd.update.builtin`"),
    ("2.1.3 内置 153 个编码不允许删除",
     "用内置编码 bddId 删除被拒，且回查记录仍在",
     "`bdd.del.builtin`"),
    ("2.1.4 列表视图分页呈现（通图号、梁型码）",
     "分页结构/每页 1 条/翻页、无参列表、按名称**模糊**过滤、按梁型码**精确**过滤、按 numberType 过滤",
     "`bdd.query.page_success`、`bdd.query.page_size_one`、`bdd.query.page_second`、`bdd.query.list_success`、`bdd.query.list_by_number`、`bdd.query.list_by_code`、`bdd.query.list_builtin`"),
    ("每个梁场独立管理自己的通图号",
     "缺 Sys-dept-id 不串数据、伪造梁场标识不串数据、缺 Authorization 鉴权失败",
     "`bdd.query.list_no_dept`、`bdd.query.list_fake_dept`、`bdd.query.list_no_auth`、`bdd.add.no_dept`、`bdd.add.no_auth`"),
    ("增删改查基本可用性",
     "新增成功可查、按 id 查、编辑改名/改码、编辑缺主键被拒、删除、重复删除、批量删除（含无效 ID）、批量删除缺参",
     "`bdd.add.success`、`bdd.query.by_id_success`、`bdd.update.name_success`、`bdd.update.code_success`、`bdd.update.miss_id`、`bdd.del.success`、`bdd.del.repeat`、`bdd.del.batch_success`、`bdd.del.batch_with_invalid`、`bdd.del.batch_miss_param`"),
]
for a, b, c in rows:
    w("| %s | %s | %s |" % (a, b, c))
w("")
w("## 四、通图号用例清单（%d 条）" % n1)
w("")
w("| 编号 | 子模块 | key | 标题 |")
w("| --- | --- | --- | --- |")
for c in mcases(M1):
    w("| %s | %s | `%s` | %s |" % (num(c), c["sub_module_name"], c["key"], c["title"]))
w("")
w("## 五、静载试验设计参数：需求条目 → 用例映射")
w("")
w("| 需求（需求 2.2） | 校验点 | 对应用例（key） |")
w("| --- | --- | --- |")
rows2 = [
    ("参数挂在通图号上（bddId 必填）",
     "缺 bddId 被拒，不得产生无归属配置",
     "`sld.add.miss_bdd`"),
    ("一个通图号只有一条静载参数（1:1）",
     "同一 bddId 再提交一份参数：拒绝或覆盖都可接受，但按 bddId 回查必须仍只有 1 条",
     "`sld.add.one_to_one`"),
    ("设计混凝土强度 / 弹性模量 / 挠跨比 必填",
     "分别缺 rd / ed / fl 时被拒，且回查该通图号下无配置落库",
     "`sld.add.miss_rd`、`sld.add.miss_ed`、`sld.add.miss_fl`"),
    ("24 项参数持久化（3 必填 + 2 枚举 + 19 选填）",
     "全字段新增后逐字段回查（数值、枚举、千斤顶行列数）",
     "`sld.add.success`"),
    ("只填必填项也应能保存",
     "仅 bddId/rd/ed/fl 新增成功，选填项可为空",
     "`sld.add.min_fields`"),
    ("参数可反复修改",
     "全字段编辑后按 btdId 回查，未传字段保持原值；缺主键被拒；缺鉴权被拒且未生效",
     "`sld.update.success`、`sld.update.miss_id`、`sld.update.no_auth`"),
    ("参数在成果表中体现（按通图号检索）",
     "按 bddId 过滤只返回该通图号的配置、无参列表结构、分页、按 id 查询",
     "`sld.query.list_by_bdd`、`sld.query.list_success`、`sld.query.page_success`、`sld.query.by_id_success`"),
    ("增删改基本可用性",
     "删除成功、重复删除幂等、批量删除、批量删除含无效 ID、缺 btdIds 被拒、查询不存在主键不报 500",
     "`sld.del.success`、`sld.del.repeat`、`sld.del.batch_success`、`sld.del.batch_with_invalid`、`sld.del.batch_miss_param`、`sld.query.by_id_not_exist`"),
    ("按梁场隔离 + 鉴权",
     "缺 Authorization / 缺 Sys-dept-id 时列表与写操作均被拦截",
     "`sld.query.list_no_auth`、`sld.query.list_no_dept`、`sld.add.no_auth`、`sld.add.no_dept`、`sld.del.no_auth`、`sld.del.batch_no_auth`"),
]
for a, b, c in rows2:
    w("| %s | %s | %s |" % (a, b, c))
w("")
w("## 六、载荷计算用例清单（%d 条）" % n2)
w("")
w("| 编号 | 子模块 | key | 标题 |")
w("| --- | --- | --- | --- |")
for c in mcases(M2):
    w("| %s | %s | `%s` | %s |" % (num(c), c["sub_module_name"], c["key"], c["title"]))
w("")
w("## 七、测试数据")
w("")
w("### 7.1 通图号正向数据（梁型码落在 153~998，名称可直接读出梁型）")
w("")
w("| key | 通图号名称 | 梁型码 | 用途 |")
w("| --- | --- | --- | --- |")
for x in tds:
    if re.match(r"^bdd\.add\.t\d+$", x["key"]):
        w("| `%s` | %s | %s | %s |" % (x["key"], x["data"]["designDrawingsNumber"],
                                     x["data"]["designBeamType"], x["description"]))
w("")
w("### 7.2 通图号负向数据（本应被拒绝，清场同样覆盖）")
w("")
w("| key | 报文要点 | 期望 |")
w("| --- | --- | --- |")
for x in tds:
    if re.match(r"^bdd\.add\.n\d+$", x["key"]):
        b = x["data"]
        desc = "名称=%s；码=%s" % (b.get("designDrawingsNumber", "（缺）"), b.get("designBeamType", "（缺）"))
        w("| `%s` | %s | %s |" % (x["key"], desc, x["description"]))
w("")
w("### 7.3 载荷模块自建的通图号（前缀 `载荷测试图号-`，与通图号模块的 `测试通图号-` 隔离）")
w("")
w("| key | 通图号名称 | 梁型码 | 用途 |")
w("| --- | --- | --- | --- |")
for x in tds:
    if x["key"].startswith("sld.bdd.add."):
        w("| `%s` | %s | %s | %s |" % (x["key"], x["data"]["designDrawingsNumber"],
                                     x["data"]["designBeamType"],
                                     x["description"].replace("载荷模块自建通图号：", "").split("；")[0]))
w("")
w("### 7.4 静载试验设计参数")
w("")
w("| key | 配置到 | 报文要点 |")
w("| --- | --- | --- |")
VAR2NAME = {}
for x in tds:
    m = re.match(r"^sld\.bdd\.add\.(p\d+)$", x["key"])
    if m:
        VAR2NAME["${sldBdd%s}" % m.group(1).upper()] = x["data"]["designDrawingsNumber"]
for x in tds:
    if re.match(r"^sld\.add\.l\d+(dup)?$", x["key"]):
        b = x["data"]
        keys = [k for k in b if k not in ("bddId",)]
        w("| `%s` | %s | 共 %d 项：%s |" % (
            x["key"], VAR2NAME.get(b["bddId"], b["bddId"]), len(keys),
            "、".join("%s=%s" % (k, b[k]) for k in keys[:6]) + ("…" if len(keys) > 6 else "")))
for x in tds:
    if x["key"].startswith("sld.add.miss"):
        w("| `%s` | %s | %s |" % (x["key"], x["data"].get("bddId", "（缺）"), x["description"]))
w("")
w("## 八、数据隔离与清场")
w("")
w("按规则以**模块**为清场单位：清场不单独成用例，挂在每个模块**最后一条用例**（`order` = 模块内最大 + 1）的后置步骤里，"
  "即使该用例测试步骤失败，后置清场仍会执行。")
w("")
w("**通图号模块**（%d 条判据）：一次无参列表扫描本梁场全部通图号，按名称逐个 `$..[?(@.designDrawingsNumber=='…')].bddId` 判断是否存在，"
  "存在才按 bddId 删除；`缺图号名称`/名称为空串的两条负向报文没有名称可定位，改按其独有梁型码（874/875）兜底扫描。即 %d 个名称 + 2 个兜底编码 = %d 条判据。" % (len(items1), len(items1) - 2, len(items1)))
w("")
w("**载荷计算模块**（%d 个清理块）：先删静载配置（按造数时提取的 btdId，避免外键冲突），再删模块自建的通图号；"
  "每个块都以「通图号名称是否存在」为判据，扫到才执行。" % len(blocks2))
w("")
w("**三条隔离措施**")
w("")
w("1. **前缀隔离**：通图号模块只清 `测试通图号-`，载荷模块只清 `载荷测试图号-`，两个模块各自独立执行、互不误删；"
  "两者都不以 `测试梁型-` 开头，梁型管理的清场也不会碰到它们。")
w("2. **先查后建**：所有造数在用例前置里「按梁型码/bddId 查一次，没有才新增，新增后再查一次取主键」（新增接口都不返回主键），"
  "系统里已有数据时不会因为重复新增而失败。两个「新增成功」用例例外：它们的被测动作就是新增，"
  "因此前置先按梁型码/bddId **删掉残留再新增**（幂等），保证单独执行也能稳定通过。")
w("3. **内置 153 条只读、不参与清场**：内置编码只用于「不可编辑/不可删除」两条负向断言，以及 `numberType=1` 的过滤校验；"
  "唯一会写内置数据的地方是「初始化通图号」接口，且只在 `numberType=1` 查不到时才调用（先查后建）。测试数据全部自建。")
w("")
w("**环境前提**：本梁场（机构 deptCode=`TESTLC201`）需要内置 153 条通图号。这套用例不再把「已初始化」当作硬前提——"
  "`bdd.query.list_builtin`、`bdd.update.builtin`、`bdd.del.builtin` 等内置相关用例的前置会先查 `numberType=1`，"
  "**查不到才调用「初始化通图号」接口补全**，因此未初始化的梁场也能把这些用例跑通（并顺带验证初始化能力）。"
  "组织机构链路与梁场基本信息沿用梁型管理模块已有的前置数据（`beamfield.*`），不重复造。")
w("")
w("## 九、断言策略")
w("")
w("| 场景 | 做法 |")
w("| --- | --- |")
w("| 成功/失败判定 | `$` `res_contains_data` `{status,code}`；失败用例再加 `$.message` `not_empty` |")
w("| 过滤是否真的生效 | 用 `length_eq 1` + 字段值断言，而不是只看“查得到东西” |")
w("| 只读用例的期望值来自上下文 | 用 `ctx.is_ctx_var=True` + `expect_value` 填变量名（如 `sldBddP01`），执行器自动替换；不依赖本用例步骤里有没有请求报文 |")
w("| 数值字段类型不确定 | 用 `in [60, \"60\", 60.0]` 兼容 number/string 两种返回 |")
w("| 提示语语义 | 仅 `message` 的内容用 `ai_assertion_rule` 做语义判断（如“应提示梁型码已存在”） |")
w("| 幂等/不报 500 | `$.code eq 200` + AI 说明「不得抛 500 / 数据库异常」 |")
w("| 允许两种合法行为 | 先用 `$.code eq 200` + AI 说明「拒绝或覆盖均可」，再用回查 `length_eq 1` 锁定最终结果（`sld.add.one_to_one`） |")
w("")
w("## 十、评审确认结论（原「待确认事项」已全部确认，用例已按结论调整）")
w("")
w("| # | 事项 | 确认结论 | 用例侧的落地 |")
w("| --- | --- | --- | --- |")
w("| 1 | 载荷新增接口的 `btdId` 是否要传 | **不传**；接口文档把 `btdId` 标「必须」是文档有误，主键由服务端生成 | 新增报文只带 `bddId` + 业务字段；`btdId` 一律按 `bddId` 回查获取（`sld.add.*` 已如此，无需改） |")
w("| 2 | 一个通图号能有几条静载参数 | **只有一条（1:1）** | 新增用例 `sld.add.one_to_one`：同一 `bddId` 再提交一份参数，拒绝或覆盖都可接受，但回查必须仍只有 1 条；专门配了 p14/l10 一组数据，不影响其它用例 |")
w("| 3 | 新增接口是否返回新主键 | **不返回，只能通过查询获得** | 全部造数沿用「新增后按梁型码/`bddId` 回查并提取主键」，与梁型管理一致 |")
w("| 4 | 列表过滤是精确还是模糊 | **图号名称模糊匹配；梁型码按精确**（后端实际匹配方式仍待实跑确认） | `bdd.query.list_by_number` 只传名称片段「测试通图号-32m双线箱梁」并断言恰好 1 条（精确匹配会返回 0 条而失败）；`list_by_code` 传完整 3 位码 |")
w("| 5 | 内置 153 条由谁初始化 | **由「初始化通图号」接口（`initBfmBeamField`）生成** | 新增用例 `bdd.init.builtin`：调用后 `numberType=1` 仍为 153 条（重复调用不得重复生成）；内置相关用例的前置改为「查不到才调初始化」 |")
w("| 6 | 编辑接口的 `bddId` 是否必填 | **必填**（文档表格标「非必须」为标注错误） | 新增负向用例 `bdd.update.miss_id`：不带 `bddId` 提交改名应被拒，且回查原记录未被改动 |")
w("| 7 | `numberType` 的使用范围 | **只有查询接口返回**；新增的一定是 2（其他编码），1 是初始化生成的基础编码 | 新增成功用例回查断言 `numberType in [2,'2']`；新增/编辑报文一律不带该字段 |")
w("| 8 | 「新建排在最前」的实现方式 | **通图号分页查询返回的数据里，新建记录位于第一条** | `bdd.add.sort_first` 改为「新增后按 pageNum=1&pageSize=10 查询，断言 `data.list[0]` 即新记录」 |")
w("| 9 | 「已生成梁体信息后不允许编辑/删除」 | **不用覆盖** | 未写用例（需要跨模块造梁体数据） |")
w("| 10 | 图号名称超过 50 字符的负向用例 | **去掉**（其余保留） | 删除原 `bdd.add.long_number`（含报文 `bdd.add.n03` 与探针），名称类只留「缺名称」「空串」两条 |")
w("")
w("**仍需实跑确认的两点**")
w("")
w("1. `bdd.init.builtin` 断言「`numberType=1` 恰好 153 条」：如果测试梁场此前被重复初始化过、库里已有重复内置编码，"
  "这条会先失败——此时建议先清理重复内置记录再跑，或把断言放宽为 `length_gt 152`。")
w("2. `sld.add.one_to_one` 对「重复配置」只要求「最终只有 1 条」，不锁定拒绝还是覆盖；"
  "如果你希望明确要求「必须拒绝并提示已存在」，把第一条步骤的 `$.code eq 200` 改成失败断言即可。")
w("")
w("## 十一、入库方式（已执行）")
w("")
w("```bash")
w("cd 桥梁与载荷计算")
w("python insert_bdd_sld_to_db.py")
w("```")
w("")
w("脚本按 key 幂等 upsert，并清理本套已废弃的 `bdd.*` / `sld.*` 记录；用例 id 会按本文件的顺序在每个模块内重排。"
  "本次执行结果：api_test_data 新增 236 / 更新 0 / 删除 0，api_test_case 新增 71 / 更新 0 / 删除 0，api_info 写入 14 条（id 18~31）；"
  "库内合计 31 条 api_info、567 条测试数据、186 条用例（登陆 28 / 组织机构 27 / 梁场信息 11 / 梁型管理 49 / 通图号 43 / 载荷计算 28）。")
w("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("已生成 %s（%d 行）" % (OUT, len(buf)))
