"""
伤停情报 Agent：获取实时伤停/停赛信息

职责：
- 并发获取两队伤停名单
- 识别关键球员缺阵（影响 xG 模型的重要输入）
- 输出关键缺阵球员清单
"""
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class InjuriesAgent:
    """伤停情报 Agent"""

    async def gather(self, team_a: str, team_b: str) -> dict[str, Any]:
        """
        并发获取两队伤停信息

        Returns:
            dict: {
                "team_a_injuries": [...],
                "team_b_injuries": [...],
                "key_players_out": [...]  # 关键球员缺阵（会影响 xG）
            }
        """
        task_a = self._fetch_team_injuries(team_a)
        task_b = self._fetch_team_injuries(team_b)

        results = await asyncio.gather(task_a, task_b, return_exceptions=True)
        inj_a: list[Any] = results[0] if not isinstance(results[0], Exception) else []  # type: ignore[assignment]
        inj_b: list[Any] = results[1] if not isinstance(results[1], Exception) else []  # type: ignore[assignment]

        if isinstance(results[0], Exception):
            logger.warning(f"伤停抓取异常 {team_a}: {results[0]}")
        if isinstance(results[1], Exception):
            logger.warning(f"伤停抓取异常 {team_b}: {results[1]}")

        return {
            "team_a_injuries": inj_a,
            "team_b_injuries": inj_b,
            "key_players_out": self._identify_key_absences(inj_a, inj_b),
        }

    async def _fetch_team_injuries(self, team: str) -> list[Any]:
        """
        抓取单队伤停信息

        数据源候选：
        - transfermarkt.com (injuries/suspensions API)
        - thephysioroom.com
        - 国内：雷速体育、懂球帝伤停接口
        """
        try:
            return [{
                "team": team,
                "injuries": [],
                "suspensions": [],
                "doubtful": [],
                "source": "placeholder",
            }]
        except Exception as e:
            logger.warning(f"伤停抓取失败 {team}: {e}")
            return []

    def _identify_key_absences(self, inj_a: list[Any], inj_b: list[Any]) -> list[Any]:
        """
        识别关键球员缺阵

        关键球员定义：
        - 首发阵容主力
        - xG 贡献 > 队内前 30%
        - 近 5 场进球/助攻者

        返回的关键缺阵将直接传入 xG 调整器 (PlayerXgAdjuster)
        """
        return []
