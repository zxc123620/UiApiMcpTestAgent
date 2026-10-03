#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/2 15:20
# Author:zhouxiaochuan
# Description:
import uuid
from threading import Thread, Event
from uuid import uuid4

import gradio as gr
from gradio import ChatMessage
from uiapimcptestagent.ai.agents.case_genrate_agent.case_generator_agents import ApiCaseGeneratorAgent


class ChatPageThread(Thread):
    """
    聊天框线程
    """
    def __init__(self):
        super().__init__(daemon=True, name="ChatPageThread")
        self.case_generate_agent = ApiCaseGeneratorAgent()
        self.gradio = gr.ChatInterface(
            self.case_generate_func,
            title="测试用例生成助手聊天框",
        )
        self.gradio_thread = Thread(
            target=self.gradio.launch,
            daemon=True,
            name="Gradio",
        )
        self.close_event = Event()

    def run(self):
        """
        运行聊天框线程
        Returns:

        """
        self.gradio_thread.start()
        self.close_event.wait()
        self.gradio_thread.join()
        print("聊天框线程已关闭")


    def close(self):
        """
        关闭聊天框线程
        """
        try:
            self.gradio.close()
        finally:
            self.close_event.set()


    def case_generate_func(self, message, history):
        """
        用例生成函数
        Returns:
        """
        try:
            last_content = ""
            response = []
            for msg_obj in self.case_generate_agent.stream(message):
                last_content = msg_obj.content
                # 如果是第一条消息，直接添加
                if len(response) == 0:
                    response.append(ChatMessage(
                        content=msg_obj.content,
                        metadata={"title": f"🤔 推理中…", "id": uuid4().hex, "status": "pending"},
                    ))
                else:
                    # 如果上一条消息内容长度小于1024，把当前消息内容拼接上一条消息内容，否则创建新消息内容
                    if len(response[-1].content) < 1024:
                        response[-1].content += msg_obj.content
                    else:
                        response.append(ChatMessage(
                            content=msg_obj.content,
                            metadata={"title": "🤔 推理中…", "id": uuid4().hex, "status": "pending"},
                        ))
                last_chat_msg = response[-1]
                if len(last_chat_msg.content) > 1024:
                    last_chat_msg.metadata["status"] = "done"
                    last_chat_msg.metadata["title"] = "✅ 推理完成"
                yield response
            response.append(ChatMessage(content=last_content))
            yield response

        except Exception as e:
            yield ChatMessage(content=f"生成失败：{e}")

if __name__ == '__main__':
    ChatPageThread().run()
    input("按任意键退出")
