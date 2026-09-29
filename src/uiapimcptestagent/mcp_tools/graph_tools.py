#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/23 17:08
# Author:zhouxiaochuan
# Description:
import json
from pathlib import Path

from fastmcp.tools import tool

from uiapimcptestagent.apps import csrd_api_mcp


class ApiGraphTool:

    @tool()
    def get_api_graph(self) -> str:
        """
        获取API依赖图
        Returns:
        """
        dependency_graph_path = Path(__file__).resolve( )/ "api_dependency_graph.json"
        with open(dependency_graph_path, "r") as f:
            import json
            dependency_graph = json.load(f)
            return json.dumps(dependency_graph)

api_graph_tool = ApiGraphTool()
csrd_api_mcp.add_tool(api_graph_tool.get_api_graph)
