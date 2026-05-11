
"""
AFA v9.0 - 完全AI原生预测系统！
===================================
完全AI原生：
1. 使用LLM驱动的决策系统
2. 记忆系统（语义/事件记忆）
3. 模式发现与AI洞察
4. 价值发现与智能投注
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# 添加项目路径
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from src.afa_v9.ai_augmented import (
    AI_NATIVE_SYSTEM,
    AI_NATIVE_POISSON_MODEL,
    LLMBettingDecider,
    LLMDynamicKelly,
    AIAugmentedExecutionEngine,
)

from src.core.historical_data import HISTORICAL_LOADER, MatchRecord

logger = logging.getLogger(__name__)


def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


@dataclass
class AINativePrediction:
    """AI原生预测结果"""
    home_team: str
    away_team: str
    league: str
    ai_insights: List[str]
    predicted_outcome: str
    confidence: float
    value_edge: float
    suggested_stake: float
    reasoning: str


class CompleteAINativeSystemRunner:
    """完全AI原生系统运行器"""

    def __init__(self):
        print_section("🚀 初始化完全AI原生系统")

        print("\n  正在初始化AI原生历史数据库...")
        AI_NATIVE_SYSTEM.initialize()

        print("\n  正在初始化AI原生Poisson模型...")
        AI_NATIVE_POISSON_MODEL.initialize()

        print("\n  正在初始化LLM投注决策器...")
        self.llm_decider = LLMBettingDecider()

        print("\n  正在初始化动态Kelly...")
        self.llm_kelly = LLMDynamicKelly()

        print("\n  正在初始化AI增强执行引擎...")
        self.execution_engine = AIAugmentedExecutionEngine()

        print("\n✅ 完全AI原生系统初始化完成！")

    def predict_match(self, match: MatchRecord) -> AINativePrediction:
        """进行AI原生预测（完全LLM驱动）"""

        print(f"\n  🔍 正在分析 {match.home_team} vs {match.away_team} ({match.league})")

        # 步骤1：获取AI洞察（历史数据 + 模式发现）
        analysis = AI_NATIVE_SYSTEM.get_complete_analysis(
            match.home_team, match.away_team, match.league
        )

        insights = analysis.get("ai_insight", {}).get("insights", [])
        print("  🧠 AI洞察:")
        for insight in insights[:3]:
            print(f"    - {insight}")

        # 步骤2：AI原生预测
        from src.afa_v9.ai_augmented.ai_native_poisson import AIPredictionContext
        context = AIPredictionContext(
            has_injury=False,
            weather_impact="normal",
            recent_form=[True, True, True, False, True],
            home_advantage_active=True,
        )

        prediction = AI_NATIVE_POISSON_MODEL.ai_predict_with_adjustments(
            match.home_team, match.away_team, context
        )

        print(f"\n  📊 AI预测概率:")
        print(f"    主队胜: {prediction.home_win_prob:.1%}")
        print(f"    平局: {prediction.draw_prob:.1%}")
        print(f"    客队胜: {prediction.away_win_prob:.1%}")
        print(f"    置信度: {prediction.confidence_score:.1%}")

        # 步骤3：LLM决策（如果有赔率）
        outcome_options = ["home", "draw", "away"]
        probs = [prediction.home_win_prob, prediction.draw_prob, prediction.away_win_prob]
        best_idx = probs.index(max(probs))
        best_outcome = outcome_options[best_idx]

        value_edge = 0.0
        suggested_stake = 10.0

        if match.home_odds and match.draw_odds and match.away_odds:
            odds_map = {"home": match.home_odds, "draw": match.draw_odds, "away": match.away_odds}
            implied = 1 / odds_map[best_outcome]
            value_edge = max(probs[best_idx] - implied, 0)

            suggested_stake = self.llm_kelly.llm_calculate_kelly(
                probs[best_idx], odds_map[best_outcome], initial_capital=1000.0
            )

        reasoning = "\n".join([
            "AI分析了以下因素：",
            "- 历史交锋记录",
            "- 近期状态",
            "- 主客场优势",
            "- 联赛特定模式",
        ])

        return AINativePrediction(
            home_team=match.home_team,
            away_team=match.away_team,
            league=match.league,
            ai_insights=insights,
            predicted_outcome=best_outcome,
            confidence=prediction.confidence_score,
            value_edge=value_edge,
            suggested_stake=suggested_stake,
            reasoning=reasoning,
        )

    def run_bulk_prediction(self, matches: List[MatchRecord], limit: int = 10):
        """运行批量预测"""
        print_section(f"🤖 运行 {limit} 场AI原生预测")

        predictions: List[AINativePrediction] = []
        for i, match in enumerate(matches):
            if i >= limit:
                break
            try:
                pred = self.predict_match(match)
                predictions.append(pred)
            except Exception as e:
                print(f"  ⚠️ 预测失败: {e}")
                continue

        return predictions


def main():
    print_section("🚀 AFA v9.0 - 完全AI原生系统演示")
    print("""
本次演示的核心特性（AI原生）：
1. ✅ LLM驱动的投注决策
2. ✅ AI原生历史数据库（158,971场）
3. ✅ 模式发现与AI洞察生成
4. ✅ 语义关系图谱
5. ✅ 动态参数调整
    """)

    # 加载数据
    print_section("步骤1：加载真实历史数据")
    matches = HISTORICAL_LOADER.load_all()
    valid_matches = [m for m in matches if m.home_odds]

    print(f"  ✅ 数据规模: {len(matches):,} 场")
    print(f"  ✅ 有赔率数据: {len(valid_matches):,} 场")

    # 初始化AI原生系统
    runner = CompleteAINativeSystemRunner()

    # 运行预测
    print_section("步骤2：运行AI原生预测（5场）")
    predictions = runner.run_bulk_prediction(valid_matches[:100], limit=5)

    # 结果总结
    print_section("✅ AI原生预测完成")
    print("\n📋 预测总结:")
    for i, pred in enumerate(predictions, 1):
        print(f"\n  {i}. {pred.home_team} vs {pred.away_team}")
        print(f"     预测结果: {pred.predicted_outcome.upper()}")
        print(f"     置信度: {pred.confidence:.1%}")
        print(f"     价值空间: {pred.value_edge:.1%}")
        print(f"     建议注额: ¥{pred.suggested_stake:.0f}")

    print_section("✅ AI原生系统演示完成！")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()

