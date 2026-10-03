#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 10:05
# Author:zhouxiaochuan
# Description:
import logging

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from uiapimcptestagent.ai.agent_factory import AgentFactory
from uiapimcptestagent.ai.llm_models.deepseek_model import deepseek_llm
from uiapimcptestagent.ai.mcp_tools.api_case_generator_tools import get_api_summary, get_api_swagger_md_text, \
    save_test_case
from uiapimcptestagent.tools.singleton import Singleton


class ApiCaseGeneratorAgent(metaclass=Singleton):
    """
    api接口测试用例生成智能体
    """

    SYSTEM_PROMPT = """
    # 角色
    你是一个接口测试用例生成智能体，你的任务是根据用户输入的API接口描述，生成对应的测试用例。
    用例生成需考虑接口:
        1、正常场景 
        2、没有鉴权。有些接口可能不需要鉴权,你需要根据接口的描述,判断是否需要鉴权,如果不需要鉴权,则不生成测试用例。
        3、 只填写必要的参数 
        4、填写全部参数 
        5、不同的枚举值 
        6、必填项为空。
    # 可用工具
    1. get_api_summary: 查询所有接口的项目、模块、子模块、API名称
    2. get_api_swagger_md_text: 查询指定接口的Swagger Markdown描述
    3. save_test_case: 保存测试用例到文件
    
    # 流程
    1. 使用工具`get_api_summary`查询一共有哪些模块的接口
    2. 从用户的输入中识别出用户需要生成用例的接口,根据第一步得到的接口摘要信息，得出用户需最终要哪些接口信息。
    3. 将第二步中得到的项目名称、模块、子模块、API名称，传递给工具`get_api_swagger_md_text`查询单个接口的详细swagger描述
    4. 根据接口的详细swagger描述，生成对应的测试用例,用例输出格式包含key,title,description,module,sub_module,
        "key": "用例的唯一标识,需要有实际意义并且不能重复,例如user.add.success标识添加用户成功测试用例",
        "title": "用例的名称,例如`添加用户成功`",
        "description": "用例的详细描述,例如`添加用户成功,用户详细信息是xxx,`",
        "module": "模块名称(中文),例如`基础信息`",
        "sub_module": "子模块名称(中文),例如`用户管理`"
    5. 如果用户提到保存测试用例,调用工具`save_test_case`保存测试用例到文件，如果没有提到保存测试用例,则不调用工具
    
    # 输出
    
    转换为自然语言进行输出,可使用表格+解释的形式来展示。
    """

    def __init__(self, instance_id: str = "CaseGeneratorAgent", thread_id: str = "CaseGeneratorAgent"):
        self.config = {"configurable": {"thread_id": thread_id}}
        self.checkpointer = InMemorySaver()
        self.agent = None

    def stream(self, content: str):
        """
        调用智能体生成测试用例
        Args:
            content: 用户输入的API接口描述

        Returns:

        """
        if self.agent is None:
            self.agent = AgentFactory.create_agent(
                llm=deepseek_llm,
                tools=[get_api_summary, get_api_swagger_md_text, save_test_case],
                system_prompt=self.SYSTEM_PROMPT,
                checkpointer=self.checkpointer,
            )

        logging.info("=" * 50)

        for chunk in self.agent.stream(
                input={"messages": [HumanMessage(content)]},
                config=self.config,
                stream_mode="updates",
        ):
            for node_name, update in chunk.items():
                for msg in update.get("messages", []):
                    yield msg
