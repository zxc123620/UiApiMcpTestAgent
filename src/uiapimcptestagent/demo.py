#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 22:18
# Author:zhouxiaochuan
# Description:
import jsonpath

from uiapimcptestagent.tools.response_model_tool import json_extract

data = {
    "status": "1",
    "code": "200",
    "message": None,
    "timestamp": 1793349710745,
    "data": [
        {
            "btId": "1c8d0cc22fd04d5d903bde71bd8aa9bc",
            "name": "测试梁型-24m单线T梁-D02",
            "beamBodyType": "1",
            "beamLengthType": "2",
            "beamLength": 24.6,
            "sjth": "d94eb72a05374f2480f1f824e8681730",
            "barrierType": "0",
            "lineType": "1",
            "zpType": "1",
            "beamLocation": "3",
            "planTotal": 64,
            "beamTypeColor": "#FF8C00",
            "tenantId": "9f31fa4f827d49d092199b35c85c9798",
            "createBy": "92b57c6bbb794f649e78ad98152a90ae",
            "createTime": "2026-10-30 16:38:24",
            "updateBy": None,
            "updateTime": None,
            "designDrawingsNumber": "通桥(2005)2221-Ⅱ",
            "designBeamType": "008",
            "hadUnion": False,
            "tenantIds": None
        },
        {
            "btId": "ea17ae312f62494e8c765ae9e0dd90c3",
            "name": "测试梁型-24m双线T梁-B05",
            "beamBodyType": "1",
            "beamLengthType": "2",
            "beamLength": 24.6,
            "sjth": "4b845f1500924e16a1cde83bb2226843",
            "barrierType": "1",
            "lineType": "2",
            "zpType": "1",
            "beamLocation": "1",
            "planTotal": 64,
            "beamTypeColor": "#BDB76B",
            "tenantId": "9f31fa4f827d49d092199b35c85c9798",
            "createBy": "92b57c6bbb794f649e78ad98152a90ae",
            "createTime": "2026-10-30 16:41:51",
            "updateBy": None,
            "updateTime": None,
            "designDrawingsNumber": "通桥(2005)2221-Ⅲ",
            "designBeamType": "009",
            "hadUnion": False,
            "tenantIds": None
        },
        {
            "btId": "b79363d89f544eebb9f14a476d1346dc",
            "name": "测试梁型-24m单线箱梁-B04",
            "beamBodyType": "2",
            "beamLengthType": "2",
            "beamLength": 24.6,
            "sjth": "4b845f1500924e16a1cde83bb2226843",
            "barrierType": "0",
            "lineType": "1",
            "zpType": "2",
            "beamLocation": None,
            "planTotal": 100,
            "beamTypeColor": "#7B68EE",
            "tenantId": "9f31fa4f827d49d092199b35c85c9798",
            "createBy": "92b57c6bbb794f649e78ad98152a90ae",
            "createTime": "2026-10-30 16:41:50",
            "updateBy": None,
            "updateTime": None,
            "designDrawingsNumber": "通桥(2005)2221-Ⅲ",
            "designBeamType": "009",
            "hadUnion": False,
            "tenantIds": None
        }
    ]
}

# btId = json_extract(data, "$..[?(@.name=='测试梁型-32m双线箱梁-A01')].btId")
btId = jsonpath.jsonpath(data, "$..[?(@.name=='测试梁型-24m单线箱梁-B04')].btId")
print(btId)
