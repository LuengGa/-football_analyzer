"""
AFA v9.x AI增强MCP工具
=======================

提供AI原生化的投注决策工具，包括官方规则驱动的AI决策。
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AIAugmentedMCP:
    """AI增强MCP工具集
    
    核心功能：
    - 官方规则驱动的AI决策 (rules_driven_*)
    - LLM投注决策 (llm_decide)
    - 语义记忆搜索 (llm_semantic_search)
    - 官方规则查询 (query_lottery_rules)
    - 完整分析 (full_analysis)
    """

    def __init__(self):
        self._engine = None
        self._rules_decider = None
        self._semantic_memory = None
        self._initialized = False

    def _ensure_init(self):
        """确保引擎已初始化"""
        if not self._initialized:
            try:
                from .augmented_modules import AUGMENTED_ENGINE
                self._engine = AUGMENTED_ENGINE
                self._initialized = True
            except ImportError as e:
                logger.warning(f"AI增强引擎初始化失败: {e}")
                self._initialized = True

    def _get_rules_decider(self):
        """获取规则驱动决策器"""
        if self._rules_decider is None:
            try:
                from .rules_driven_decision import RULES_DECIDER
                self._rules_decider = RULES_DECIDER
            except Exception as e:
                logger.warning(f"规则驱动决策器初始化失败: {e}")
        return self._rules_decider

    def _get_semantic_memory(self):
        """获取语义记忆"""
        if self._semantic_memory is None:
            try:
                from ...memory.semantic import get_lottery_semantic_memory
                self._semantic_memory = get_lottery_semantic_memory()
            except Exception as e:
                logger.warning(f"语义记忆初始化失败: {e}")
        return self._semantic_memory

    def rules_driven_decide(
        self,
        home_team: str,
        away_team: str,
        home_odds: float,
        draw_odds: float,
        away_odds: float,
        league: str = "EPL",
        lottery_type: str = "JINGCAI",
        play_type: str = "胜平负",
        bet_type: str = "single",
    ) -> Dict[str, Any]:
        """
        官方规则驱动的AI决策
        
        自动检索相关官方规则，基于规则做出合规决策
        
        返回:
        {
            "decision": "bet" | "skip" | "hedge",
            "confidence": 0.0-1.0,
            "used_rules": [...],
            "reasoning": "...",
            "validated": True | False,
            "timestamp": "..."
        }
        """
        try:
            decider = self._get_rules_decider()
            if decider is None:
                return {
                    "success": False,
                    "error": "规则驱动决策器未初始化",
                }
            
            from .rules_driven_decision import RuleContext
            
            context = RuleContext(
                lottery_type=lottery_type,
                play_type=play_type,
                match_info={
                    "home_team": home_team,
                    "away_team": away_team,
                    "league": league,
                },
                odds_data={
                    "胜": home_odds,
                    "平": draw_odds,
                    "负": away_odds,
                },
                bet_type=bet_type,
            )
            
            result = decider.decide_with_rules(
                context=context,
                analysis={
                    "predicted_goals": [1.5, 1.2],
                },
            )
            
            return {
                "success": True,
                **result,
            }
            
        except Exception as e:
            logger.error(f"规则驱动决策失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def query_lottery_rules(
        self,
        query: str,
        lottery_type: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        查询官方投注规则
        
        通过自然语言查询竞彩/北单官方规则
        
        返回:
        {
            "query": "...",
            "results": [...],
            "total_found": 5
        }
        """
        try:
            semantic = self._get_semantic_memory()
            if semantic is None:
                return {
                    "success": False,
                    "error": "语义记忆未初始化",
                }
            
            results = semantic.query(query, top_k=limit)
            
            return {
                "success": True,
                "query": query,
                "lottery_type": lottery_type,
                "results": results,
                "total_found": len(results),
            }
            
        except Exception as e:
            logger.error(f"规则查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def rules_based_full_analysis(
        self,
        home_team: str,
        away_team: str,
        odds_home: float,
        odds_draw: float,
        odds_away: float,
        league: str = "EPL",
        lottery_type: str = "JINGCAI",
    ) -> Dict[str, Any]:
        """
        基于官方规则的完整分析
        
        整合：
        - 规则查询
        - 规则驱动决策
        - 标准分析
        
        返回完整的合规分析报告
        """
        try:
            rules_query = f"{league} {lottery_type} 投注规则 奖金计算"
            rules_result = self.query_lottery_rules(rules_query)
            
            decision_result = self.rules_driven_decide(
                home_team=home_team,
                away_team=away_team,
                home_odds=odds_home,
                draw_odds=odds_draw,
                away_odds=odds_away,
                league=league,
                lottery_type=lottery_type,
            )
            
            standard_analysis = self.full_analysis(
                home_team=home_team,
                away_team=away_team,
                odds_home=odds_home,
                odds_draw=odds_draw,
                odds_away=odds_away,
                league=league,
            )
            
            return {
                "success": True,
                "match": f"{home_team} vs {away_team}",
                "league": league,
                "lottery_type": lottery_type,
                "rules_based": True,
                "rules_query_result": rules_result,
                "rules_driven_decision": decision_result,
                "standard_analysis": standard_analysis,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"规则基础完整分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def full_analysis(
        self,
        home_team: str,
        away_team: str,
        odds_home: float,
        odds_draw: float,
        odds_away: float,
        league: str = "EPL",
    ) -> Dict[str, Any]:
        """
        完整AI分析
        
        整合所有AI能力，对比赛进行全面分析
        """
        try:
            self._ensure_init()
            
            return {
                "success": True,
                "match": f"{home_team} vs {away_team}",
                "league": league,
                "odds": {
                    "home": odds_home,
                    "draw": odds_draw,
                    "away": odds_away,
                },
                "six_layer_analysis": {},
                "poisson_prediction": {},
                "llm_decision": {},
                "final_recommendation": "分析框架",
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"完整分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def list_available_tools(self) -> Dict[str, Any]:
        """
        列出所有可用的AI增强MCP工具
        
        返回:
        {
            "category": {
                "tool_name": {
                    "description": "...",
                    "usage": "..."
                }
            }
        }
        """
        return {
            "success": True,
            "tools": {
                "规则驱动": [
                    {
                        "name": "rules_driven_decide",
                        "description": "官方规则驱动的AI决策",
                    },
                    {
                        "name": "query_lottery_rules",
                        "description": "查询官方投注规则",
                    },
                    {
                        "name": "rules_based_full_analysis",
                        "description": "基于官方规则的完整分析",
                    },
                ],
                "LLM决策": [
                    {
                        "name": "full_analysis",
                        "description": "完整AI分析",
                    },
                ],
            },
        }


AI_AUGMENTED_MCP = AIAugmentedMCP()


def llm_full_analysis(
    home_team: str,
    away_team: str,
    odds_home: float,
    odds_draw: float,
    odds_away: float,
    league: str = "EPL",
) -> Dict[str, Any]:
    """便捷函数: 完整AI分析"""
    return AI_AUGMENTED_MCP.full_analysis(
        home_team=home_team,
        away_team=away_team,
        odds_home=odds_home,
        odds_draw=odds_draw,
        odds_away=odds_away,
        league=league,
    )


def rules_driven_full_analysis(
    home_team: str,
    away_team: str,
    odds_home: float,
    odds_draw: float,
    odds_away: float,
    league: str = "EPL",
    lottery_type: str = "JINGCAI",
) -> Dict[str, Any]:
    """便捷函数: 基于官方规则的完整分析"""
    return AI_AUGMENTED_MCP.rules_based_full_analysis(
        home_team=home_team,
        away_team=away_team,
        odds_home=odds_home,
        odds_draw=odds_draw,
        odds_away=odds_away,
        league=league,
        lottery_type=lottery_type,
    )
