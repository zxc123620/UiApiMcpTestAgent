#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/7 12:31
# Author:zhouxiaochuan
# Description:

from uiapimcptestagent.ai.agents.base_agent import BaseAgent
# from uiapimcptestagent.ai.ai_res_model.test_assert_res_model import ApiTestAssertResModel


class TestAssertAgent(BaseAgent):
    """
    测试用例断言智能体
    """

    SYSTEM_PROMPT = """
    你是断言裁判。从用户输入的【预期结果】和【实际结果】中判断【实际结果】是否在语义(如有)、数据内容(如有)、数据格式(如有)上满足【预期结果】。
    判断标准：
    - 只要实际结果表达了预期结果的含义就算通过
    - 不要求文字完全一致
    - 如果实际结果缺少预期结果要求的关键信息，则失败
    
    只输出 JSON：
    {"pass_": true 或 false, "reason": "一句话说明理由"}
    """

    def __init__(self, instance_id: str = "TestAssertAgent", thread_id: str = "TestAssertAgent"):
        BaseAgent.__init__(self, instance_id=instance_id, thread_id=thread_id)
