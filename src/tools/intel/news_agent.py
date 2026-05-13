"""
新闻情报 Agent：抓取比赛相关新闻

职责：
- 并发获取两队最新新闻
- 识别交叉新闻（同时涉及两队：转会、恩怨、历史交锋等）
- 输出结构化新闻摘要供下游决策使用
"""
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class NewsAgent:
    """新闻情报 Agent"""

    async def gather(self, team_a: str, team_b: str) -> dict[str, Any]:
        """
        并发获取两队新闻，返回聚合结果

        Args:
            team_a: 主队名称
            team_b: 客队名称

        Returns:
            dict: {
                "team_a_news": [...],
                "team_b_news": [...],
                "cross_news": [...]  # 同时涉及两队的新闻
            }
        """
        task_a = self._fetch_team_news(team_a)
        task_b = self._fetch_team_news(team_b)

        results = await asyncio.gather(task_a, task_b, return_exceptions=True)
        news_a: list[Any] = results[0] if not isinstance(results[0], Exception) else []  # type: ignore[assignment]
        news_b: list[Any] = results[1] if not isinstance(results[1], Exception) else []  # type: ignore[assignment]

        if isinstance(results[0], Exception):
            logger.warning(f"新闻抓取异常 {team_a}: {results[0]}")
        if isinstance(results[1], Exception):
            logger.warning(f"新闻抓取异常 {team_b}: {results[1]}")

        return {
            "team_a_news": news_a,
            "team_b_news": news_b,
            "cross_news": self._find_cross_news(news_a, news_b),
        }

    async def _fetch_team_news(self, team: str) -> list[Any]:
        """
        抓取单队新闻

        实际实现应调用新闻 API（如虎扑、懂球帝、ESPN 等），
        当前为模拟实现，保留原有 DDGS 搜索能力。
        """
        try:
            from duckduckgo_search import DDGS

            results: list[dict[str, Any]] = []
            with DDGS() as ddgs:
                for r in ddgs.text(f"{team} football news today", max_results=3):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", ""),
                    })
            return [{"team": team, "articles": results}]
        except ImportError:
            logger.debug(f"DDGS 未安装，跳过 {team} 新闻抓取")
            return []
        except Exception as e:
            logger.warning(f"新闻抓取失败 {team}: {e}")
            return []

    def _find_cross_news(self, news_a: list[Any], news_b: list[Any]) -> list[Any]:
        """
        找出同时涉及两队的新闻（转会、恩怨、历史交锋等）

        当前为骨架实现，后续可接入 NLP 相似度匹配。
        """
        return []
