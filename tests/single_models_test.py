import openai
import yaml
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置SSL证书路径
os.environ['SSL_CERT_FILE'] = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'certifi', 'cacert.pem')

def test_model(config):
    try:
        # 替换环境变量
        base_url = os.path.expandvars(config['base_url'])
        api_key = os.path.expandvars(config['api_key'])
        
        client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": "Hi"}],
            timeout=10
        )
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    print(f'\n开始测试模型连通性 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    
    # 定义要测试的模型配置
    test_configs = [

        {
            'model': 'abab6-chat',
            'base_url': '${VOAPI_BASE_URL}',
            'api_key': '${VOAPI_API_KEY}',
            'timeout': 60,
            'max_retries': 3
        }
    ]

    for cfg in test_configs:
        print('\n' + '='*50)
        print(f"测试模型: {cfg['model']}")
        print(f"基础URL: {cfg['base_url']}")
        
        success, error = test_model(cfg)
        if success:
            print("✓ 连接成功")
        else:
            print(f"✗ 连接失败: {error}")

if __name__ == '__main__':
    main()