"""
AFA v9.0 浏览器自动化引擎
===========================

支持多种浏览器自动化方案:
1. agent-browser (推荐，无需LLM)
2. browser-use (需要支持视觉的LLM)
3. Playwright (传统方案)
4. 直接HTTP请求 (无头方案)

自动选择可用方案
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BrowserEngine(ABC):
    """浏览器引擎基类"""
    
    @abstractmethod
    async def extract(self, url: str, instruction: str) -> str:
        """从页面提取信息"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        pass


class AgentBrowserEngine(BrowserEngine):
    """
    agent-browser 引擎
    ===================
    
    基于 Chrome CDP 的浏览器自动化工具
    优点: 无需 LLM API，直接控制浏览器
    安装: npm install -g agent-browser
    """
    
    def __init__(self):
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return bool(self._available)

        import shutil
        self._available = shutil.which("agent-browser") is not None
        return bool(self._available)
    
    async def extract(self, url: str, instruction: str) -> str:
        """使用 agent-browser 提取页面信息"""
        if not self.is_available():
            return "Error: agent-browser not installed"
        
        import subprocess
        import json
        
        try:
            cmd = [
                "agent-browser",
                "open", url,
                "&&", "agent-browser", "wait", "--load", "networkidle",
                "&&", "agent-browser", "get", "text", "body"
            ]
            
            result = subprocess.run(
                " && ".join(cmd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def search_and_extract(self, query: str) -> str:
        """使用 agent-browser 搜索"""
        if not self.is_available():
            return "Error: agent-browser not installed"
        
        import subprocess
        
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            cmd = f'''
            agent-browser open "{search_url}" && \
            agent-browser wait --load networkidle && \
            agent-browser snapshot -i && \
            agent-browser get text body
            '''
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error: {str(e)}"


class BrowserUseEngine(BrowserEngine):
    """
    browser-use 引擎
    ================
    
    基于 AI 的浏览器自动化，需要支持视觉的 LLM
    支持: OpenAI GPT-4o, DeepSeek VL, Claude, etc.
    """
    
    def __init__(self, llm=None):
        self._llm = llm
        self._agent_cls = None
    
    def is_available(self) -> bool:
        try:
            from browser_use import Agent
            return True
        except ImportError:
            return False
    
    def _get_llm(self):
        """获取可用的 LLM"""
        if self._llm:
            return self._llm
        
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if deepseek_key:
            try:
                from langchain_deepseek import ChatDeepSeek
                return ChatDeepSeek(
                    model="deepseek-chat",
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com",
                )
            except ImportError:
                pass
        
        if openai_key:
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4o",
                    api_key=openai_key,
                )
            except ImportError:
                pass
        
        return None
    
    async def extract(self, url: str, instruction: str) -> str:
        """使用 AI 驱动浏览器"""
        if not self.is_available():
            return "Error: browser-use not installed"
        
        llm = self._get_llm()
        if not llm:
            return "Error: No LLM available (set DEEPSEEK_API_KEY or OPENAI_API_KEY)"
        
        try:
            from browser_use import Agent
            
            full_task = f"""
            1. 打开网页: {url}
            2. 等待页面加载完成
            3. 执行任务: {instruction}
            4. 返回提取的数据
            """
            
            agent = Agent(task=full_task, llm=llm)
            history = await agent.run()
            
            if history and hasattr(history, 'final_result'):
                return str(history.final_result())  # type: ignore[no-any-return]
            return str(history)
            
        except Exception as e:
            return f"Error: {str(e)}"


class PlaywrightEngine(BrowserEngine):
    """
    Playwright 引擎
    ==============
    
    传统浏览器自动化，适合结构化数据抓取
    """
    
    def __init__(self):
        self._available = None
        self._browser = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return bool(self._available)

        try:
            from playwright.sync_api import sync_playwright
            self._available = True
        except ImportError:
            self._available = False

        return bool(self._available)

    async def extract(self, url: str, instruction: str) -> str:
        """使用 Playwright 提取"""
        if not self.is_available():
            return "Error: playwright not installed (pip install playwright)"
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                
                content = page.content()
                
                if instruction:
                    try:
                        elements = page.query_selector_all("table, div.odds, .score")
                        data = []
                        for el in elements[:10]:
                            data.append(el.inner_text())
                        return "\n".join(data) if data else content[:5000]
                    except:
                        pass

                browser.close()
                return str(content[:5000])
                
        except Exception as e:
            return f"Error: {str(e)}"


class HttpEngine(BrowserEngine):
    """
    HTTP 请求引擎
    =============
    
    无头方案，直接发送 HTTP 请求获取页面
    最轻量，但不执行 JavaScript
    """
    
    def __init__(self):
        self._session = None
    
    def is_available(self) -> bool:
        return True
    
    async def extract(self, url: str, instruction: str) -> str:
        """直接请求页面"""
        import requests
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            lines = [line for line in text.split("\n") if line]
            
            return "\n".join(lines[:200])
            
        except Exception as e:
            return f"Error: {str(e)}"


class UnifiedBrowser:
    """
    统一浏览器引擎
    ==============
    
    自动选择最优可用方案
    优先级: agent-browser > browser-use > playwright > http
    """
    
    def __init__(self):
        self.engines: list[BrowserEngine] = []
        self._init_engines()
    
    def _init_engines(self):
        """初始化所有可用引擎"""
        engines = [
            AgentBrowserEngine(),
            BrowserUseEngine(),
            PlaywrightEngine(),
            HttpEngine(),
        ]
        
        for engine in engines:
            if engine.is_available():
                self.engines.append(engine)
                logger.info(f"✓ 浏览器引擎可用: {engine.__class__.__name__}")
    
    @property
    def primary_engine(self) -> Optional[BrowserEngine]:
        """获取首选引擎"""
        return self.engines[0] if self.engines else None
    
    async def extract(self, task_instruction: str, url: str = None) -> str:
        """
        提取页面信息
        
        Args:
            task_instruction: 自然语言任务指令
            url: 目标URL，如果为None则执行搜索
        
        Returns:
            提取的文本内容
        """
        if not self.engines:
            return "Error: No browser engine available"
        
        errors = []
        
        for engine in self.engines:
            try:
                target_url = url
                
                if not target_url and "搜索" in task_instruction:
                    from urllib.parse import quote
                    query = task_instruction.replace("搜索", "").strip()
                    search_url = f"https://www.google.com/search?q={quote(query)}"
                    target_url = search_url
                
                if not target_url:
                    target_url = "https://www.google.com"
                
                logger.info(f"使用引擎: {engine.__class__.__name__}")
                result = await engine.extract(target_url, task_instruction)
                
                if not result.startswith("Error:"):
                    return result
                else:
                    errors.append(f"{engine.__class__.__name__}: {result}")
                    
            except Exception as e:
                errors.append(f"{engine.__class__.__name__}: {str(e)}")
                continue
        
        return f"All engines failed:\n" + "\n".join(errors)
    
    async def search(self, query: str) -> str:
        """搜索并提取结果"""
        return await self.extract(f"搜索: {query}")


# 全局实例
BROWSER = UnifiedBrowser()


def get_browser() -> UnifiedBrowser:
    """获取浏览器实例"""
    return BROWSER


# 便捷函数
async def extract_info(task_instruction: str, url: str = None) -> str:
    """提取信息"""
    browser = get_browser()
    return await browser.extract(task_instruction, url)


async def search_web(query: str) -> str:
    """搜索网络"""
    browser = get_browser()
    return await browser.search(query)
