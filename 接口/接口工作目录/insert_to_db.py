# -*- coding: utf-8 -*-
"""
将 梁型管理-接口测试用例.json 同步到 test_data.db（可重复执行）
- api_info：按 id 更新（10~17），不存在则按该 id 新增
- api_test_data / api_test_case：按 key 更新，key 不存在则新增（id 顺延 MAX(id)+1）
- 同步后清掉本模块（api_info 10~17 / module_name=梁型管理）在库中但已不在 JSON 里的记录，
  使删掉的用例真正从库内消失；不影响其它模块的数据。
"""
import io
import json
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = "D:/code/UiApiMcpTestAgent/test_data.db"
SRC = os.path.join(BASE, "梁型管理-接口测试用例.json")


def j(v):
    return None if v is None else json.dumps(v, ensure_ascii=False)


def main():
    d = json.load(io.open(SRC, encoding="utf-8"))
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys=ON")
    cur = con.cursor()

    ins_td = upd_td = ins_cs = upd_cs = 0
    try:
        for a in d["api_info"]:
            row = (a["name"], a["project_name"], a["module_name"], a["sub_module_name"],
                   a["description"], a["endpoint"], a["method"], a["response_model"],
                   a["swagger_md_text"])
            cur.execute(
                "UPDATE api_info SET name=?,project_name=?,module_name=?,sub_module_name=?,"
                "description=?,endpoint=?,method=?,response_model=?,swagger_md_text=? WHERE id=?",
                row + (a["id"],))
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO api_info (name,project_name,module_name,sub_module_name,description,"
                    "endpoint,method,response_model,swagger_md_text,id) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    row + (a["id"],))

        next_td = cur.execute("SELECT COALESCE(MAX(id),0)+1 FROM api_test_data").fetchone()[0]
        for x in d["api_test_data"]:
            row = (x["name"], x["description"], j(x["headers"]), x["api_info_id"],
                   j(x["data"]), j(x["params"]), j(x["extract"]))
            cur.execute(
                'UPDATE api_test_data SET name=?,description=?,headers=?,api_info_id=?,'
                '"data"=?,params=?,"extract"=? WHERE "key"=?', row + (x["key"],))
            if cur.rowcount == 0:
                cur.execute(
                    'INSERT INTO api_test_data (id,"key",name,description,headers,api_info_id,'
                    '"data",params,"extract") VALUES (?,?,?,?,?,?,?,?,?)',
                    (next_td, x["key"]) + row)
                next_td += 1
                ins_td += 1
            else:
                upd_td += 1

        next_cs = cur.execute("SELECT COALESCE(MAX(id),0)+1 FROM api_test_case").fetchone()[0]
        for x in d["api_test_case"]:
            row = (x["module_name"], x["sub_module_name"], x["title"], x["description"],
                   j(x["pre_requisites"]), j(x["test_steps"]), x["is_active"], j(x["post_steps"]),
                   x.get("order", 0))
            cur.execute(
                'UPDATE api_test_case SET module_name=?,sub_module_name=?,title=?,description=?,'
                'pre_requisites=?,test_steps=?,is_active=?,post_steps=?,"order"=? WHERE "key"=?',
                row + (x["key"],))
            if cur.rowcount == 0:
                cur.execute(
                    'INSERT INTO api_test_case (id,"key",module_name,sub_module_name,title,description,'
                    'pre_requisites,test_steps,is_active,post_steps,"order") VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    (next_cs, x["key"]) + row)
                next_cs += 1
                ins_cs += 1
            else:
                upd_cs += 1

        # 清理本模块已废弃的记录（JSON 中已不存在的 key）
        td_keys = {x["key"] for x in d["api_test_data"]}
        case_keys = {x["key"] for x in d["api_test_case"]}
        api_ids = {a["id"] for a in d["api_info"]}

        ph = ",".join("?" * len(api_ids))
        stale_td = [r[0] for r in cur.execute(
            'SELECT "key" FROM api_test_data WHERE api_info_id IN (%s)' % ph,
            tuple(api_ids)).fetchall() if r[0] not in td_keys]
        stale_cs = [r[0] for r in cur.execute(
            'SELECT "key" FROM api_test_case WHERE module_name=?', ("梁型管理",)).fetchall()
            if r[0] not in case_keys]

        for k in stale_td:
            cur.execute('DELETE FROM api_test_data WHERE "key"=?', (k,))
        for k in stale_cs:
            cur.execute('DELETE FROM api_test_case WHERE "key"=?', (k,))

        # 按 JSON 中的用例顺序重排本模块用例 id：
        # order 相同时按 id 兜底排序，重排后兜底顺序与 JSON 一致
        # （终局清场的 order 由 JSON 给出模块内最大值，确保最后执行）
        cur_rows = cur.execute(
            'SELECT id, "key" FROM api_test_case WHERE module_name=?', ("梁型管理",)).fetchall()
        id_by_key = {k: i for i, k in cur_rows}
        ordered_keys = [x["key"] for x in d["api_test_case"]]
        start = min(id_by_key[k] for k in ordered_keys)
        target = {k: start + idx for idx, k in enumerate(ordered_keys)}
        if any(id_by_key[k] != target[k] for k in ordered_keys):
            off = 1000000  # 先挪到临时区避免主键冲突，再落回目标 id
            for k in ordered_keys:
                cur.execute("UPDATE api_test_case SET id=? WHERE id=?", (off + target[k], id_by_key[k]))
            for k in ordered_keys:
                cur.execute("UPDATE api_test_case SET id=? WHERE id=?", (target[k], off + target[k]))
            print("已按用例逻辑顺序重排 id：%d~%d" % (start, start + len(ordered_keys) - 1))

        con.commit()
    except Exception:
        con.rollback()
        raise

    print("同步完成：api_info %d 条；api_test_data 更新 %d / 新增 %d / 删除 %d；"
          "api_test_case 更新 %d / 新增 %d / 删除 %d" % (
              len(d["api_info"]), upd_td, ins_td, len(stale_td),
              upd_cs, ins_cs, len(stale_cs)))
    if stale_td or stale_cs:
        print("已删除废弃记录：%s" % ", ".join(stale_td + stale_cs))
    con.close()


if __name__ == "__main__":
    main()
