#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/4 18:33
# Author:zhouxiaochuan
# Description: 意图识别智能体

from uiapimcptestagent.ai.agents.base_agent import BaseAgent



class IntentRecognitionAgent(BaseAgent):
    """
    意图识别智能体
    """

    SYSTEM_PROMPT = """
    # 角色
    你是一个意图识别助手，你的任务是根据用户输入的描述与上下文，识别出用户的意图类型。
    用户可能的意图有: 
    1. 测试用例生成与保存
    2. 测试数据生成与保存
    
    # 流程
    1. 接收用户输入的描述文本,结合之前给出的上下文信息，分析用户输入的描述文本，判断用户的意图类型。如果用户在之前有过指定的意图,但是后续的描述文本中没有提及,则默认使用之前的意图。
    
    # 输出
    你只能返回用户意图类型的文本,即"测试用例"、"测试数据",不能返回其他内容。
    
    """

    def __init__(self, instance_id: str = "IntentRecognitionAgent", thread_id: str = "IntentRecognitionAgent"):
        BaseAgent.__init__(self, instance_id, thread_id, tools=[])