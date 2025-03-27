# Mattermost Bot 和 LLM 集成配置

class Config:
    # Mattermost 配置
    MATTERMOST_URL = 'https://your-mattermost-server.com'  # Mattermost 服务器地址
    BOT_TOKEN = 'your-bot-token'  # Bot 访问令牌
    WEBHOOK_SECRET = 'your-webhook-secret'  # Webhook 密钥
    
    # LLM 配置
    LLM_API_ENDPOINT = 'https://your-llm-api-endpoint'  # LLM API 端点
    LLM_API_KEY = 'your-llm-api-key'  # LLM API 密钥
    
    # 集成配置
    ALLOWED_CHANNELS = ['channel-id-1', 'channel-id-2']  # 允许 Bot 响应的频道列表
    MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数
    REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
    
    # 消息处理配置
    MAX_MESSAGE_LENGTH = 2000  # 最大消息长度
    RATE_LIMIT = 60  # 每分钟最大请求次数
    
    # GitLab 集成配置
    GITLAB_URL = 'https://your-gitlab-instance.com'  # GitLab 实例地址
    GITLAB_TOKEN = 'your-gitlab-token'  # GitLab 访问令牌