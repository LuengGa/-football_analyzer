"""
AFA LLM配置文件

请填入您的API配置：
1. SiliconFlow（硅基流动）：https://api.siliconflow.cn
2. OpenAI：https://api.openai.com/v1
3. 其他兼容API

API Key获取地址：
- SiliconFlow: https://siliconflow.cn
- OpenAI: https://platform.openai.com
"""

LLM_CONFIG = {
    # 必填：API地址
    "base_url": "https://api.siliconflow.cn/v1",
    
    # 必填：API Key（请替换为您的真实API Key）
    "api_key": "YOUR_API_KEY_HERE",
    
    # 模型选择
    "model": "Qwen/Qwen2.5-7B-Instruct",
    
    # 可选参数
    "temperature": 0.7,
    "max_tokens": 2000,
}

# 可用模型推荐（SiliconFlow）
MODELS = {
    "Qwen2.5-7B": "Qwen/Qwen2.5-7B-Instruct",
    "Qwen2.5-14B": "Qwen/Qwen2.5-14B-Instruct", 
    "DeepSeek-V2.5": "deepseek-ai/DeepSeek-V2.5",
    "GLM-4": "THUDM/glm-4-9b-chat",
}
