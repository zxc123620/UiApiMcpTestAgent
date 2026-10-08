#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:37
# Author:zhouxiaochuan
# Description:
import os

from langchain_mcp_adapters.client import MultiServerMCPClient

PORT = int(os.getenv("PORT", 8099))

local_client = MultiServerMCPClient({
    "my-server": {
        "url": f"http://localhost:{PORT}/mcp",
        "transport": "streamable_http",  # 或 "sse"
    }
})