"""
AFA v9.0 浏览器自动化工具
==========================

支持多种搜索/抓取方式:
1. HTTP搜索 - 无头，快速，适合简单页面
2. Playwright - 完整浏览器，支持JS渲染
3. browser-use - AI驱动(需配置LLM)

使用优先级: HTTP > Playwright > browser-use
"""

import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def search_web(query: str) -> str:
    """
    搜索网页 - HTTP方式

    Args:
        query: 搜索关键词

    Returns:
        搜索结果文本
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
        }

        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&mkt=en-US"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        results = []
        for item in soup.select('li.b_algo')[:15]:
            title_el = item.select_one('h2 a')
            snippet_el = item.select_one('p')
            if title_el:
                title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                snippet = snippet_el.get_text(strip=True) if snippet_el else ''
                results.append(f"【{title}】\n   {snippet[:150]}...\n   🔗 {link[:80]}")

        return '\n\n'.join(results) if results else "未找到结果"

    except requests.exceptions.RequestException as e:
        logger.warning(f"搜索请求失败: {e}")
        return f"搜索失败: {str(e)}"


class VisualBrowser:
    """
    Playwright浏览器 - 用于访问需要JS渲染的页面
    """

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def extract_info(self, task_instruction: str) -> str:
        """
        访问指定URL并提取信息

        Args:
            task_instruction: 自然语言指令，包含URL或搜索词

        Returns:
            提取的页面内容
        """
        try:
            from playwright.async_api import async_playwright

            url = None
            search_term = None

            url_match = re.search(r'https?://[^\s)]+', task_instruction)
            search_match = re.search(r'搜索[：:]\s*(.+)', task_instruction)

            if url_match:
                url = url_match.group(0).rstrip(').,')
            elif search_match:
                search_term = search_match.group(1).strip()
            else:
                return "请提供URL或搜索词"

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
                page = await browser.new_page(viewport={"width": 1280, "height": 720})

                if url:
                    logger.info(f"访问: {url}")
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                else:
                    return str(search_web(search_term) if search_term else "")

                content = await self._extract_content(page, task_instruction)
                await browser.close()

            return content

        except Exception as e:
            logger.error(f"浏览器提取失败: {e}")
            return f"Error: {str(e)}"

    async def _extract_content(self, page, instruction: str) -> str:
        """提取页面内容"""
        try:
            body = await page.query_selector('body')
            if body:
                text = await body.inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
                return '\n'.join(lines[:200])
            return "无法提取内容"
        except Exception as e:
            return f"提取失败: {e}"

    async def close(self):
        """关闭浏览器"""
        pass


async def extract_info(task_instruction: str) -> str:
    """
    提取页面信息 - 便捷函数

    自动选择最佳方式
    """
    search_match = re.search(r'搜索[：:]\s*(.+)', task_instruction)
    if search_match and 'https://' not in task_instruction:
        return search_web(search_match.group(1).strip())

    browser = VisualBrowser()
    try:
        return await browser.extract_info(task_instruction)
    finally:
        await browser.close()


if __name__ == "__main__":
    import asyncio

    async def test():
        print("=== 搜索测试 ===\n")

        query = "Arsenal vs Chelsea betting odds"
        print(f"搜索: {query}\n")

        result = search_web(query)
        print(result[:1500] if result else "无结果")

        print("\n=== 测试完成 ===")

    asyncio.run(test())
