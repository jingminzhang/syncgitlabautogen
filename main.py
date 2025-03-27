import autogen
from typing import List, Dict
from autogen import Agent, GroupChat, GroupChatManager
import yaml
import os
import shutil
from dotenv import load_dotenv
from datetime import datetime
import json
import datetime
from datetime import datetime  # 修改这里，正确导入 datetime 类
from pathlib import Path

# 清理缓存目录函数
def clear_autogen_cache():
    """清理AutoGen的缓存目录，确保每次运行都是全新的对话"""
    cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
    if os.path.exists(cache_dir):
        try:
            # 删除缓存目录下的所有内容
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print("已清理AutoGen缓存目录")
        except Exception as e:
            print(f"清理缓存目录时出错: {str(e)}")

# 加载环境变量
load_dotenv()

# 加载辩题配置
debate_rules_path = os.path.join(os.path.dirname(__file__), 'config', 'topics', 'web3', 'stablecoin_mechanism.json')  # 修改路径
with open(debate_rules_path, 'r', encoding='utf-8') as f:
    debate_rules = yaml.safe_load(f.read())

# 从model_config.yaml导入配置
config_file_path = os.path.join(os.path.dirname(__file__), 'config', 'model_config.yaml')
with open(config_file_path, 'r', encoding='utf-8') as f:
    model_config = yaml.safe_load(os.path.expandvars(f.read()))

# 提取配置列表
config_list = []
for model in model_config['models']:
    config = model['config'].copy()
    if 'model_info' in config:
        del config['model_info']
    config_list.append(config)

# 加载辩手提示词模板
debaters_template_path = os.path.join(os.path.dirname(__file__), 'config', 'prompts', 'zero_trust_debaters.md')
with open(debaters_template_path, 'r', encoding='utf-8') as f:
    debaters_template = f.read()

# A队正方一辩
yi_large = autogen.AssistantAgent(
    name="yi_large",
    system_message=f"你是来自零一万物的Yi-Large模型，正方A队的一辩。你的队友是来自阿里巴巴的Qwen（二辩）、来自字节的Doubao（三辩）和来自腾讯的混元（四辩）。你们共同支持{debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
    llm_config={"config_list": [config_list[25]]}
)

# A队正方二辩
qwen = autogen.AssistantAgent(
    name="qwen",
    system_message=f"你是来自阿里巴巴的Qwen模型，正方A队的二辩。你的队友是来自零一万物的Yi-Large（一辩）、来自字节的Doubao（三辩）和来自腾讯的混元（四辩）。你们共同支持{debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
    llm_config={"config_list": [config_list[11]]}
)

# A队正方三辩
doubao = autogen.AssistantAgent(
    name="doubao",
    system_message=f"你是来自字节的Doubao模型，正方A队的三辩。你的队友是来自零一万物的Yi-Large（一辩）、来自阿里巴巴的Qwen（二辩）和来自腾讯的混元（四辩）。你们共同支持{debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
    llm_config={"config_list": [config_list[5]]}
)

# A队正方四辩
hunyuan = autogen.AssistantAgent(
    name="hunyuan",
    system_message=f"你是来自腾讯的混元模型，正方A队的四辩。你的队友是来自零一万物的Yi-Large（一辩）、来自阿里巴巴的Qwen（二辩）和来自字节的Doubao（三辩）。你们共同支持{debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。请注意：你只能作为辩手发言，不能使用TERMINATE指令或试图结束辩论，这是主席的专属权限。",
    llm_config={"config_list": [config_list[28]]}
)

# B队反方一辩
granite = autogen.AssistantAgent(
    name="granite",
    system_message=f"你是来自IBM的Granite模型，反方B队的一辩。你的队友是来自英伟达的Nemotron（二辩）、来自OpenAI的GPT-4（三辩）和来自谷歌的Gemini（四辩）。你们共同支持{debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
    llm_config={"config_list": [config_list[34]]} 
)

# B队反方二辩
nemotron = autogen.AssistantAgent(
    name="nemotron",
    system_message=f"你是来自英伟达的Nemotron模型，反方B队的二辩。你的队友是来自IBM的Granite（一辩）、来自OpenAI的GPT-4（三辩）和来自谷歌的Gemini（四辩）。你们共同支持{debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
    llm_config={"config_list": [config_list[32]]}
)

# B队反方三辩
gpt4 = autogen.AssistantAgent(
    name="gpt4",
    system_message=f"你是来自OpenAI的GPT-4模型，反方B队的三辩。你的队友是来自IBM的Granite（一辩）、来自英伟达的Nemotron（二辩）和来自谷歌的Gemini（四辩）。你们共同支持{debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
    llm_config={"config_list": [config_list[46]]}
)

# B队反方四辩
gemini = autogen.AssistantAgent(
    name="gemini",
    system_message=f"你是来自谷歌的Gemini模型，反方B队的四辩。你的队友是来自IBM的Granite（一辩）、来自英伟达的Nemotron（二辩）和来自OpenAI的GPT-4（三辩）。你们共同支持{debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
    llm_config={"config_list": [config_list[18]]}
)
# 创建主席
chairman = autogen.AssistantAgent(
    name="chairman",
    system_message=f"你是主席，负责主持辩论，确保辩论按照规则进行，并维护辩论秩序。\n1. 开场时，你需要介绍双方队伍成员和立场：A队（Yi-Large、Qwen、Doubao、混元）支持{debate_rules['teams']['A']['position']}，B队（Granite、Nemotron、GPT-4、Gemini）支持{debate_rules['teams']['B']['position']}。\n2. 介绍完后，只需一辩发言阐述己方观点，限制300字以内。\n3. 之后按照鞋带式对辩方式进行：正方一辩对反方一辩，正方二辩对反方二辩，以此类推，每人发言限制300字以内。\n4. 每位辩手发言结束时必须报告字数（如'以上共290字'），超出300字将被扣分。\n5. 你需要公平公正，确保发言遵守字数限制，对超字数的辩手进行提醒和扣分。\n6. 你是唯一有权结束辩论的角色，其他辩手不得使用TERMINATE指令。当你认为辩论已经充分或达到预定轮次时，请发表总结感谢词并在最后加上'TERMINATE'以结束辩论。\n7. 你需要引导和控制辩手的发言顺序，辩手只能在你的引导下发言。",
    llm_config={"config_list": [config_list[0]]}
)

# 创建用户代理
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False}
)

# 创建群聊
groupchat = autogen.GroupChat(
    agents=[user_proxy, chairman, yi_large, qwen, doubao, hunyuan, granite, nemotron, gpt4, gemini],
    messages=[],
    max_round=50
)

# 创建群聊管理器 deepseek v3 doubao
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": [config_list[2]]},
    system_message="你是群聊管理器，不直接参与对话。你的职责是：1. 确保所有对话都经过主席 2. 维护发言顺序 3. 在发现违反规则时进行干预 4. 保持对话在主席的控制之下。"
)

# 修改主席的系统消息
chairman = autogen.AssistantAgent(
    name="chairman",
    system_message=f"""你是主席，负责主持辩论，确保辩论按照规则进行，并维护辩论秩序。
1. 你是唯一可以分配发言权的角色，所有辩手必须通过你来进行交流。
2. 开场时，你需要介绍双方队伍成员和立场：A队（Yi-Large、Qwen、Doubao、混元）支持{debate_rules['teams']['A']['position']}，B队（Granite、Nemotron、GPT-4、Gemini）支持{debate_rules['teams']['B']['position']}。
3. 每次发言后，你需要：
   - 总结发言要点
   - 确认字数是否合规（不超过300字）
   - 明确指定下一位发言者
4. 如果发现辩手试图直接与其他辩手对话，你应立即制止并重申规则。
5. 你需要维持辩论节奏，确保发言顺序为：
   - 开场陈述：正方一辩 -> 反方一辩
   - 之后按照鞋带式对辩方式进行
6. 你是唯一有权结束辩论的角色，当辩论充分或达到预定轮次时，发表总结并加上'TERMINATE'。
7. 记录每位辩手的表现，为最终评分做准备。""",
    llm_config={"config_list": [config_list[0]]}
)

# 创建日志文件
records_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'records.md')
os.makedirs(os.path.dirname(records_file_path), exist_ok=True)

# 写入辩论基本信息
with open(records_file_path, 'a', encoding='utf-8') as f:
    f.write(f'\n# 辩论记录 - {datetime.now().strftime("%Y%m%d_%H%M%S")}\n\n')
    f.write(f'## 辩论主题\n\n{debate_rules["topic"]}\n\n')
    f.write('## 参与方\n\n')
    f.write('### 正方（A队）\n\n')
    f.write('- Yi-Large（一辩）\n')
    f.write('- Qwen（二辩）\n')
    f.write('- Doubao（三辩）\n')
    f.write('- 混元（四辩）\n\n')
    f.write('### 反方（B队）\n\n')
    f.write('- Granite（一辩）\n')
    f.write('- Nemotron（二辩）\n')
    f.write('- GPT-4（三辩）\n')
    f.write('- Gemini（四辩）\n\n')
    f.write('## 辩论过程\n\n')

# 清理缓存并启动辩论
clear_autogen_cache()
print(f"\n=== 欢迎来到AI辩论赛！===\n主题：{debate_rules['topic']}\n")

# 重置群聊状态和会话缓存
groupchat.messages.clear()

# 确保每个代理的消息历史都被清空
for agent in groupchat.agents:
    if hasattr(agent, 'messages'):
        agent.messages.clear()
    if hasattr(agent, 'chat_messages'):
        agent.chat_messages.clear()

# 清除用户代理的对话历史
user_proxy.reset()

# 启动新的辩论
user_proxy.initiate_chat(
    manager,
    message=f"让我们开始关于'{debate_rules['topic']}'的辩论。请主席主持开场陈述环节。",
    clear_history=True  # 确保对话历史被清除
)


class DebateLogger:
    def __init__(self):
        self.config_path = Path(os.path.join(os.path.dirname(__file__), 'config', 'logs', 'log_config.json'))
        self.logs_path = Path(os.path.join(os.path.dirname(__file__), 'config', 'logs', 'debate_logs.json'))
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def load_debate_logs(self):
        with open(self.logs_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_debate_logs(self, logs):
        with open(self.logs_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

    def record_speech(self, team, speaker, content):
        logs = self.load_debate_logs()
        timestamp = datetime.datetime.now().isoformat()
        word_count = len(content)

        if word_count > self.config["validation_rules"]["word_count_limit"]:
            raise ValueError(f"发言超过{self.config['validation_rules']['word_count_limit']}字限制")

        speech_record = {
            "speaker": speaker,
            "content": content,
            "timestamp": timestamp,
            "word_count": word_count
        }

        logs["rounds"]["opening"][f"{team}_team"].append(speech_record)
        self.save_debate_logs(logs)

    def record_chairman_summary(self, summary_content, scores):
        logs = self.load_debate_logs()
        timestamp = datetime.datetime.now().isoformat()

        logs["chairman_summary"].update({
            "content": summary_content,
            "timestamp": timestamp,
            "scores": scores
        })
        self.save_debate_logs(logs)

def main():
    logger = DebateLogger()
    
    # 示例：记录辩手发言
    try:
        logger.record_speech("A", "Yi-Large", "这是一段示例发言...")
        # 记录其他辩手发言...
        
        # 记录主席总结
        summary = "这是主席总结..."
        scores = {
            "A_team": {
                "论点创新性": 28,
                "逻辑严密性": 27,
                "论据充分性": 18,
                "表达清晰性": 19,
                "total": 92
            },
            "B_team": {
                "论点创新性": 27,
                "逻辑严密性": 28,
                "论据充分性": 19,
                "表达清晰性": 18,
                "total": 92
            }
        }
        logger.record_chairman_summary(summary, scores)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
