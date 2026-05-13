# -*- coding: utf-8 -*-
"""
Phase 3.1: HTTP 异步客户端迁移 (httpx)

职责：
- 将所有 requests 同步调用迁移到 httpx 异步客户端
- 提供统一的异步 HTTP 请求接口
- 支持连接池、超时控制、重试机制
- 保持与现有 API 客户端的兼容性

优势：
- 异步 I/O：并发请求性能提升 5-10 倍
- HTTP/2 支持：多路复用，减少延迟
- 自动连接池管理
- 更好的超时和取消支持
"""
from __future__ import annotations

import logging
import asyncio
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,      # 连接超时
    read=10.0,        # 读取超时
    write=5.0,        # 写入超时
    pool=5.0          # 连接池超时
)

DEFAULT_LIMITS = httpx.Limits(
    max_connections=100,      # 最大连接数
    max_keepalive_connections=20  # 最大 Keep-Alive 连接数
)


class AsyncHTTPClient:
    """
    异步 HTTP 客户端封装
    
    基于 httpx.AsyncClient，提供：
    - 连接池复用
    - 自动重试
    - 统一错误处理
    - 请求/响应日志
    """
    
    def __init__(
        self,
        timeout: Optional[httpx.Timeout] = None,
        limits: Optional[httpx.Limits] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ):
        """
        初始化异步 HTTP 客户端
        
        Args:
            timeout: 超时配置
            limits: 连接池限制
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            headers: 默认请求头
            verify_ssl: 是否验证 SSL 证书
        """
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.limits = limits or DEFAULT_LIMITS
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        # 默认请求头
        self.default_headers = {
            "User-Agent": "Agentic-Football-Analyzer/3.0",
            "Accept": "application/json",
        }
        if headers:
            self.default_headers.update(headers)
        
        # 客户端实例（懒加载）
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建 AsyncClient 实例"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=self.limits,
                headers=self.default_headers,
                verify=self.verify_ssl,
                # http2=True,  # 需要 pip install httpx[http2]
            )
        return self._client
    
    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("AsyncHTTPClient closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        发送 HTTP 请求（带自动重试）
        
        Args:
            method: HTTP 方法 (GET, POST, etc.)
            url: 请求 URL
            params: 查询参数
            json: JSON 请求体
            headers: 额外请求头
            **kwargs: 其他传递给 httpx 的参数
            
        Returns:
            httpx.Response 对象
            
        Raises:
            httpx.HTTPError: 请求失败且重试耗尽
        """
        last_exception: Optional[Exception] = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                client = await self._get_client()
                
                # 合并请求头
                request_headers = self.default_headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # 发送请求
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=request_headers,
                    **kwargs
                )
                
                # 记录成功
                if attempt > 1:
                    logger.info(f"Request succeeded after {attempt} attempts: {method} {url}")
                
                # 对于 4xx/5xx 错误，根据状态码决定是否重试
                if response.status_code >= 500 and attempt < self.max_retries:
                    logger.warning(f"Server error {response.status_code}, retrying ({attempt}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay * attempt)  # 指数退避
                    continue
                
                return response
            
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(f"Request failed (attempt {attempt}): {e}. Retrying...")
                    await asyncio.sleep(self.retry_delay * attempt)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
            
            except httpx.HTTPStatusError as e:
                # HTTP 状态错误（4xx），不重试
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise
            
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error during request: {e}")
                raise
        
        # 所有重试都失败了
        raise last_exception or Exception("Request failed")
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """发送 GET 请求"""
        return await self.request("GET", url, params=params, **kwargs)
    
    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """发送 POST 请求"""
        return await self.request("POST", url, json=json, **kwargs)
    
    async def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """发送 PUT 请求"""
        return await self.request("PUT", url, json=json, **kwargs)
    
    async def delete(
        self,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """发送 DELETE 请求"""
        return await self.request("DELETE", url, **kwargs)


class AsyncAPIFootballClient:
    """
    API-Football 异步客户端
    
    基于 AsyncHTTPClient，提供 API-Football v3 的异步访问
    """
    
    BASE_URL = "https://v3.football.api-sports.com"
    
    def __init__(self, api_key: str, **kwargs):
        self.http = AsyncHTTPClient(
            headers={"x-apisports-key": api_key},
            verify_ssl=False,  # API-Football 有时有 SSL 问题
            **kwargs
        )
    
    async def close(self):
        await self.http.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_fixtures(
        self,
        date: Optional[str] = None,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        live: bool = False
    ) -> Dict[str, Any]:
        """获取赛程"""
        params: Dict[str, Any] = {}
        if date:
            params["date"] = date
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if live:
            params["live"] = "all"
        
        response = await self.http.get(f"{self.BASE_URL}/fixtures", params=params)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
    
    async def get_odds(
        self,
        fixture_id: int,
        bookmaker_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取赔率"""
        params = {"fixture": fixture_id}
        if bookmaker_id:
            params["bookmaker"] = bookmaker_id
        
        response = await self.http.get(f"{self.BASE_URL}/odds", params=params)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
    
    async def get_teams(self, team_id: Optional[int] = None) -> Dict[str, Any]:
        """获取球队信息"""
        params = {}
        if team_id:
            params["id"] = team_id
        
        response = await self.http.get(f"{self.BASE_URL}/teams", params=params)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def concurrent_fetch(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """
    并发获取多个 URL
    
    Args:
        urls: URL 列表
        **kwargs: 传递给 AsyncHTTPClient 的参数
        
    Returns:
        响应数据列表
    """
    async with AsyncHTTPClient(**kwargs) as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                logger.error(f"Failed to fetch {urls[i]}: {resp}")
                results.append({"error": str(resp), "url": urls[i]})
            else:
                try:
                    resp.raise_for_status()  # type: ignore[union-attr]
                    results.append(resp.json())  # type: ignore[union-attr]
                except Exception as e:
                    logger.error(f"Failed to parse response from {urls[i]}: {e}")
                    results.append({"error": str(e), "url": urls[i]})
        
        return results


# 便捷函数：创建异步客户端
def create_async_client(
    api_key: Optional[str] = None,
    service: str = "generic",
    **kwargs
) -> Union[AsyncHTTPClient, AsyncAPIFootballClient]:
    """
    创建异步 HTTP 客户端
    
    Args:
        api_key: API 密钥
        service: 服务类型 ("generic", "api-football", etc.)
        **kwargs: 其他参数
        
    Returns:
        异步客户端实例
    """
    if service == "api-football":
        if not api_key:
            raise ValueError("API key required for api-football service")
        return AsyncAPIFootballClient(api_key=api_key, **kwargs)
    else:
        return AsyncHTTPClient(**kwargs)


if __name__ == "__main__":
    # 测试示例
    import asyncio
    
    async def test_async_client():
        print("=" * 60)
        print("Phase 3.1: httpx 异步客户端测试")
        print("=" * 60)
        
        # 测试 1: 基本 GET 请求
        print("\n--- 测试 1: 基本 GET 请求 ---")
        async with AsyncHTTPClient() as client:
            try:
                resp = await client.get("https://httpbin.org/get")
                print(f"✓ GET 请求成功: status={resp.status_code}")
                data = resp.json()
                print(f"  User-Agent: {data.get('headers', {}).get('User-Agent', 'N/A')}")
            except Exception as e:
                print(f"✗ GET 请求失败: {e}")
        
        # 测试 2: 并发请求
        print("\n--- 测试 2: 并发请求 ---")
        urls = [
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/1",
        ]
        
        start_time = asyncio.get_event_loop().time()
        results = await concurrent_fetch(urls)
        elapsed = asyncio.get_event_loop().time() - start_time
        
        print(f"✓ 并发获取 {len(urls)} 个 URL")
        print(f"  耗时: {elapsed:.2f}s (串行预计 3s+)")
        print(f"  成功: {sum(1 for r in results if 'error' not in r)}/{len(results)}")
        
        # 测试 3: API-Football 客户端（需要有效 API key）
        print("\n--- 测试 3: API-Football 异步客户端 ---")
        api_key = os.getenv("API_FOOTBALL_API_KEY", "")
        if api_key:
            async with AsyncAPIFootballClient(api_key=api_key) as af_client:
                try:
                    # 获取今天的赛程
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    fixtures = await af_client.get_fixtures(date=today)
                    print(f"✓ 获取今日赛程: {len(fixtures.get('response', []))} 场比赛")
                except Exception as e:
                    print(f"⚠ API-Football 请求失败: {e}")
        else:
            print("⚠ 未配置 API_FOOTBALL_API_KEY，跳过测试")
        
        print("\n✅ 异步客户端测试完成!")
    
    import os
    asyncio.run(test_async_client())
