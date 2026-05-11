"""
AFA LLM集成模块 - 支持 Ollama Cloud

Ollama Cloud 让云端模型像本地Ollama一样使用
API地址：https://ollama.com/v1
"""

import os
import json
from typing import Optional, List, Dict, Any
from openai import OpenAI
import time


class LLMConfig:
    """LLM配置"""
    def __init__(
        self,
        base_url: str = "https://ollama.com/v1",
        api_key: str = "452974588c0d4979864348443103f9b9.VbOuM-zfljhU21j8HqxSyg83",
        model: str = "qwen2.5",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens


class LLMClient:
    """LLM客户端"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig(
                base_url=os.getenv("OLLAMA_CLOUD_URL", "https://ollama.com/v1"),
                api_key=os.getenv("OLLAMA_API_KEY", "452974588c0d4979864348443103f9b9.VbOuM-zfljhU21j8HqxSyg83"),
                model=os.getenv("OLLAMA_MODEL", "qwen2.5"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "2000"))
            )
        self.config = config
        
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=120.0
        )
        
        print(f"   -> 🤖 [LLM] 已连接: {config.base_url}")
        print(f"   -> 🤖 [LLM] 模型: {config.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """发送聊天请求"""
        if system_prompt:
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
        else:
            full_messages = messages
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=full_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"   -> ❌ [LLM] API调用失败: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """简化版生成接口"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt=system)


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取全局LLM客户端（单例）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client():
    """重置全局LLM客户端"""
    global _llm_client
    _llm_client = None


def test_llm_connection() -> bool:
    """测试LLM连接"""
    try:
        client = get_llm_client()
        response = client.generate("请用中文回复'连接成功'")
        print(f"   -> ✅ [LLM] 测试响应: {response[:200]}...")
        return True
    except Exception as e:
        print(f"   -> ❌ [LLM] 连接测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("测试 Ollama Cloud 连接")
    print("=" * 60)
    
    test_llm_connection()
