from typing import List, Dict
from autogen import Agent, GroupChat, GroupChatManager, AssistantAgent, UserProxyAgent
import yaml
import os
from dotenv import load_dotenv
from datetime import datetime

class DebateManager:
    def __init__(self):
        # 辩论状态
        self.current_round = 0
        self.current_speaker = None
        self.debate_state = {
            'round': 0,
            'speaker': None,
            'messages': [],
            'last_message_time': None
        }
        # 加载环境变量
        load_dotenv()
        
        # 加载辩题配置
        self.debate_rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'topics', 'web3', 'dex_nft_narrative.json')
        with open(self.debate_rules_path, 'r', encoding='utf-8') as f:
            self.debate_rules = yaml.safe_load(f.read())

        # 从model_config.yaml导入配置
        self.config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'model_config.yaml')
        with open(self.config_file_path, 'r', encoding='utf-8') as f:
            self.model_config = yaml.safe_load(os.path.expandvars(f.read()))

        # 提取配置列表
        self.config_list = []
        for model in self.model_config['models']:
            config = model['config'].copy()
            if 'model_info' in config:
                del config['model_info']
            self.config_list.append(config)

        # 初始化所有Agent
        self.agents = self.init_agents()
        
        # 创建用户代理
        self.user_proxy = self.create_user_proxy()
        
        # 创建群聊和管理器
        self.groupchat = self.create_groupchat()
        self.manager = self.create_manager()

    def init_agents(self):
        # 加载辩手提示词模板
        debaters_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'prompts', 'debaters.md')
        with open(debaters_template_path, 'r', encoding='utf-8') as f:
            debaters_template = f.read()

        # A队正方一辩
        yi_large = AssistantAgent(
            name="yi_large",
            system_message=f"你是来自零一万物的Yi-Large模型，正方A队的一辩。你的队友是来自阿里巴巴的Qwen（二辩）、来自字节的Doubao（三辩）和来自腾讯的混元（四辩）。你们共同支持{self.debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
            llm_config={"config_list": [self.config_list[14]]}
        )

        # A队正方二辩
        qwen = AssistantAgent(
            name="qwen",
            system_message=f"你是来自阿里巴巴的Qwen模型，正方A队的二辩。你的队友是来自零一万物的Yi-Large（一辩）、来自字节的Doubao（三辩）和来自腾讯的混元（四辩）。你们共同支持{self.debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
            llm_config={"config_list": [self.config_list[1]]}
        )

        # A队正方三辩
        doubao = AssistantAgent(
            name="doubao",
            system_message=f"你是来自字节的Doubao模型，正方A队的三辩。你的队友是来自零一万物的Yi-Large（一辩）、来自阿里巴巴的Qwen（二辩）和来自腾讯的混元（四辩）。你们共同支持{self.debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。",
            llm_config={"config_list": [self.config_list[3]]}
        )

        # A队正方四辩
        hunyuan = AssistantAgent(
            name="hunyuan",
            system_message=f"你是来自腾讯的混元模型，正方A队的四辩。你的队友是来自零一万物的Yi-Large（一辩）、来自阿里巴巴的Qwen（二辩）和来自字节的Doubao（三辩）。你们共同支持{self.debate_rules['teams']['A']['position']}。你的对手是来自IBM的Granite（反方一辩）、来自英伟达的Nemotron（反方二辩）、来自OpenAI的GPT-4（反方三辩）和来自谷歌的Gemini（反方四辩）。请注意：你只能作为辩手发言，不能使用TERMINATE指令或试图结束辩论，这是主席的专属权限。",
            llm_config={"config_list": [self.config_list[0]]}
        )

        # B队反方一辩
        granite = AssistantAgent(
            name="granite",
            system_message=f"你是来自IBM的Granite模型，反方B队的一辩。你的队友是来自英伟达的Nemotron（二辩）、来自OpenAI的GPT-4（三辩）和来自谷歌的Gemini（四辩）。你们共同支持{self.debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
            llm_config={"config_list": [self.config_list[15]]}
        )

        # B队反方二辩
        nemotron = AssistantAgent(
            name="nemotron",
            system_message=f"你是来自英伟达的Nemotron模型，反方B队的二辩。你的队友是来自IBM的Granite（一辩）、来自OpenAI的GPT-4（三辩）和来自谷歌的Gemini（四辩）。你们共同支持{self.debate_rules['teams']['B']['position']}。你的对手是来自零一万物的Yi-Large（正方一辩）、来自阿里巴巴的Qwen（正方二辩）、来自字节的Doubao（正方三辩）和来自腾讯的混元（正方四辩）。",
            llm_config={"config_list": [self.config_list[8]]}
        )

        # B队反方三辩
        gpt4 = AssistantAgent(
            name="gpt4",
            system_message="你是反方B队的三辩，来自OpenAI的GPT-4模型。你需要支持{}".format(self.debate_rules['teams']['B']['position']),
            llm_config={"config_list": [self.config_list[6]]}
        )

        # B队反方四辩
        gemini = AssistantAgent(
            name="gemini",
            system_message="你是反方B队的四辩，来自谷歌的Gemini模型。你需要支持{}".format(self.debate_rules['teams']['B']['position']),
            llm_config={"config_list": [self.config_list[2]]}
        )

        # 创建主席
        chairman = AssistantAgent(
            name="chairman",
            system_message=f"你是主席，负责主持辩论，确保辩论按照规则进行，并维护辩论秩序。\n1. 开场时，你需要介绍双方队伍成员和立场：A队（Yi-Large、Qwen、Doubao、混元）支持{self.debate_rules['teams']['A']['position']}，B队（Granite、Nemotron、GPT-4、Gemini）支持{self.debate_rules['teams']['B']['position']}。\n2. 介绍完后，只需一辩发言阐述己方观点，限制300字以内。\n3. 之后按照鞋带式对辩方式进行：正方一辩对反方一辩，正方二辩对反方二辩，以此类推，每人发言限制300字以内。\n4. 每位辩手发言结束时必须报告字数（如'以上共290字'），超出300字将被扣分。\n5. 你需要公平公正，确保发言遵守字数限制，对超字数的辩手进行提醒和扣分。\n6. 当你认为辩论已经充分或达到预定轮次时，请发表总结感谢词并在最后加上'TERMINATE'以结束辩论。",
            llm_config={"config_list": [self.config_list[0]]}
        )

        return yi_large, qwen, doubao, hunyuan, granite, nemotron, gpt4, gemini, chairman

    def create_user_proxy(self):
        user_proxy = UserProxyAgent(
            name="user_proxy",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"use_docker": False},
            system_message="",
            human_input_mode="NEVER"
        )
        
        # 添加消息处理器
        async def message_handler(message):
            if isinstance(message, dict) and "content" in message:
                speaker = message.get("name", "Unknown")
                content = message["content"]
                if hasattr(self, "send_message") and callable(self.send_message):
                    await self.send_message(speaker, content)
            return True
        
        user_proxy.register_reply(
            message_handler,
            lambda x: True
        )
        
        return user_proxy

    async def message_callback(self, message):
        """处理消息回调，用于将消息同步到Web界面"""
        if isinstance(message, dict) and "content" in message:
            speaker = message.get("name", "Unknown")
            content = message["content"]
            
            # 发送消息到Web界面
            if hasattr(self, "send_message") and callable(self.send_message):
                await self.send_message(speaker, content)

    def create_groupchat(self):
        return GroupChat(
            agents=[self.user_proxy] + list(self.agents),
            messages=[],
            max_round=50
        )

    def create_manager(self):
        manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config={"config_list": [self.config_list[16]]}
        )
        
        # 重写run_stream方法以支持状态恢复
        original_run_stream = manager.run_stream
        async def run_stream_with_state(*args, **kwargs):
            # 恢复之前的状态
            if self.debate_state['messages']:
                self.groupchat.messages = self.debate_state['messages']
                self.current_round = self.debate_state['round']
                self.current_speaker = self.debate_state['speaker']
            
            # 运行对话
            async for msg in original_run_stream(*args, **kwargs):
                # 更新状态
                if hasattr(msg, 'source'):
                    self.current_speaker = msg.source
                if isinstance(msg, dict) and 'content' in msg:
                    self.debate_state['messages'] = self.groupchat.messages
                    self.debate_state['round'] = self.current_round
                    self.debate_state['speaker'] = self.current_speaker
                    self.debate_state['last_message_time'] = datetime.now()
                yield msg
        
        manager.run_stream = run_stream_with_state
        return manager

    def create_log_file(self):
        # 创建日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', f'debate_{timestamp}.md')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # 写入辩论基本信息
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f'# 辩论记录 - {timestamp}\n\n')
            f.write(f'## 辩论主题\n\n{self.debate_rules["topic"]}\n\n')
            f.write('## 参与方\n\n')
            f.write('### 正方（A队）\n\n')
            f.write('- Yi-Large（一辩）\n')
            f.write('- Qwen（二辩）\n')
            f.write('- Doubao（三辩）\n')
            f.write('- Baichuan（四辩）\n\n')
            f.write('### 反方（B队）\n\n')
            f.write('- abad6.5s（一辩）\n')
            f.write('- step-2-16k（二辩）\n')
            f.write('- GPT-4（三辩）\n')
            f.write('- Gemini（四辩）\n\n')
            f.write('## 辩论过程\n\n')