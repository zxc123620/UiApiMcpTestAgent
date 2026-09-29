
```
mcp-test-agent/
│
├── README.md
├── pyproject.toml                  # 项目依赖和构建配置
├── .env.example                    # 环境变量模板
├── .gitignore
│
├── config/                         # 配置层
│   ├── settings.py                 # 全局配置（BASE_URL、超时、重试等）
│   └── logging.yaml                # 日志配置
│
├── graph/                          # 图谱层：描述接口依赖关系
│   ├── dependency_graph.json       # 全局依赖图谱（接口级）
│   ├── modules.json                # 模块定义（哪些接口属于哪个模块）
│   └── schema.py                   # 图谱的 Pydantic 模型，校验图谱格式
│
├── cases/                          # 用例层：你写的测试用例
│   ├── api/                        # 接口用例
│   │   ├── create_user_normal.yaml
│   │   ├── create_user_invalid_role.yaml
│   │   └── user_management_module.yaml
│   └── ui/                         # UI 用例
│       └── login_flow.yaml
│
├── tools/                          # 工具层：MCP Tool 实现
│   ├── __init__.py
│   ├── api_tools.py                # call_api、assert_response
│   ├── graph_tools.py              # resolve_dependency、build_module_plan
│   ├── extract_tools.py            # extract_from_list、resolve_path
│   ├── resource_tools.py           # ensure_resource
│   ├── context_tools.py            # get/set_cached_context
│   ├── ui_tools.py                 # Playwright 相关 UI 操作
│   └── report_tools.py             # 生成测试报告
│
├── server/                         # MCP Server 入口
│   ├── __init__.py
│   ├── main.py                     # FastMCP 实例，注册所有工具和资源
│   ├── resources.py                # MCP Resource 定义（图谱查询）
│   └── registry.py                 # 工具注册中心
│
├── agent/                          # 智能体层：编排逻辑
│   ├── __init__.py
│   ├── planner.py                  # 根据用例生成执行计划
│   ├── executor.py                 # 按计划调用工具执行
│   ├── parser.py                   # 解析 YAML 用例和自然语言输入
│   └── reporter.py                 # 汇总执行结果，生成报告
│
├── core/                           # 核心逻辑：不依赖 MCP 的纯 Python 实现
│   ├── __init__.py
│   ├── graph_resolver.py           # 依赖链解析、拓扑排序
│   ├── extractor.py                # 列表提取逻辑
│   ├── http_client.py              # httpx 封装
│   ├── context.py                  # 上下文缓存（token、role_id 等）
│   └── exceptions.py               # 自定义异常
│
├── ui/                             # UI 测试相关（如果和接口测试分开放）
│   ├── __init__.py
│   ├── browser.py                  # Playwright 浏览器管理
│   └── page_actions.py             # 页面操作封装
│
├── tests/                          # 你自己的单元测试
│   ├── test_graph_resolver.py
│   ├── test_extractor.py
│   ├── test_api_tools.py
│   └── test_planner.py
│
├── scripts/                        # 辅助脚本
│   ├── validate_graph.py           # 校验图谱格式
│   ├── run_case.py                 # 命令行执行单个用例
│   └── start_server.py             # 启动 MCP Server
│
└── docs/                           # 文档
    ├── graph_schema.md             # 图谱字段说明
    ├── tool_reference.md           # 工具清单和参数说明
    └── case_format.md              # 用例 YAML 格式说明
```