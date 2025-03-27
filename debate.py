import chainlit as cl
from debate_core import DebateManager
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_core import CancellationToken

class DebateApp(DebateManager):
    def __init__(self):
        super().__init__()

@cl.on_chat_start
async def start():
    try:
        # 初始化辩论应用
        app = DebateApp()
        
        # 设置消息发送回调
        async def send_message(speaker, content):
            await cl.Message(
                content=content,
                author=speaker
            ).send()
        
        # 将消息发送函数注入到应用中
        app.send_message = send_message
        
        # 存储到会话状态
        cl.user_session.set("manager", app.manager)
        cl.user_session.set("user_proxy", app.user_proxy)

        # 创建消息元素
        elements = []
        elements.append(cl.Text(name="debate_topic", content=app.debate_rules['topic']))
        
        # 发送初始消息
        await cl.Message(
            content="欢迎来到AI辩论赛！这是一场关于零信任领域未来发展的精彩辩论。\n注意：这是一个只读的浏览模式，您可以观看辩论的全过程，但不能参与其中。",
            elements=elements
        ).send()
        
        # 启动辩论
        message = TextMessage(
            content=f"让我们开始关于'{app.debate_rules['topic']}'的辩论。请主席主持开场陈述环节。",
            source="user"
        )
        
        # 处理消息流
        streaming_response = None
        try:
            async for msg in app.manager.run_stream(messages=[message], cancellation_token=CancellationToken()):
                if isinstance(msg, ModelClientStreamingChunkEvent):
                    # Stream the model client response to the user
                    if streaming_response is None:
                        # Start a new streaming response
                        streaming_response = cl.Message(content="", author=msg.source)
                    await streaming_response.stream_token(msg.content)
                elif streaming_response is not None:
                    # Done streaming the model client response
                    await streaming_response.send()
                    streaming_response = None
                elif isinstance(msg, TaskResult):
                    # Send the task termination message
                    final_message = "辩论结束。"
                    if msg.stop_reason:
                        final_message += msg.stop_reason
                    await cl.Message(content=final_message).send()
                    break
                else:
                    # Skip all other message types
                    pass
        except Exception as e:
            error_msg = f"消息处理过程中发生错误: {str(e)}"
            await cl.Message(content=error_msg).send()
            print(error_msg)
    except Exception as e:
        error_msg = f"消息处理过程中发生错误: {str(e)}"
        await cl.Message(content=error_msg).send()
        print(error_msg)

# 启动应用
if __name__ == "__main__":
    cl.run()