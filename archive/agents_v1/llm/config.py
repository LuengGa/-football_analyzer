"""
AFA LLM配置文件

支持多LLM Provider配置，优先级：
1. 环境变量 (最高)
2. 本地配置
3. 默认值

环境变量：
- OLLAMA_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
- DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
- OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

import os

def _get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

OLLAMA_API_KEY = _get_env("OLLAMA_API_KEY", "ollama_api_key_placeholder")
OLLAMA_BASE_URL = _get_env("OLLAMA_BASE_URL", "https://ollama.com/v1")
OLLAMA_MODEL = _get_env("OLLAMA_MODEL", "deepseek-v4-flash")

DEEPSEEK_API_KEY = _get_env("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = _get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = _get_env("DEEPSEEK_MODEL", "deepseek-chat")

OPENAI_API_KEY = _get_env("OPENAI_API_KEY", "")
OPENAI_BASE_URL = _get_env("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = _get_env("OPENAI_MODEL", "gpt-4o-mini")

OLLAMA_CLOUD_CONFIG = {
    "base_url": OLLAMA_BASE_URL,
    "api_key": OLLAMA_API_KEY,
    "model": OLLAMA_MODEL,
    "temperature": 0.7,
    "max_tokens": 4000,
}

AVAILABLE_PROVIDERS = ["ollama", "deepseek", "openai"]

AVAILABLE_CLOUD_MODELS = [
    "qwen2.5",
    "deepseek-v3.1",
    "deepseek-v4-flash",
    "llama3.1",
]
