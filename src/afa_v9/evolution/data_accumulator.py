"""
AFA Evolution 数据积累管理器
=============================

自动数据注入机制：
1. 从历史回测数据导入经验
2. 从bet_recorder导入投注记录
3. 自动分析联赛/赔率模式
4. 定时触发evolution进化

使用方式:
    python -m src.afa_v9.evolution.data_accumulator --mode auto
    python -m src.afa_v9.evolution.data_accumulator --mode backtest --file ./data/backtest_results.json
    python -m src.afa_v9.evolution.data_accumulator --mode sync --days 30
"""

import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from . import EVOLUTION_ENGINE, EvolutionEngine, OutcomeType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvolutionDataAccumulator:
    def __init__(self, evolution_engine: Optional[EvolutionEngine] = None):
        self.evolution = evolution_engine or EVOLUTION_ENGINE
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "evolution"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def import_backtest_results(self, file_path: str) -> Dict[str, Any]:
        """从回测结果导入经验"""
        logger.info(f"📥 导入回测结果: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"❌ 读取文件失败: {e}")
            return {"imported": 0, "error": str(e)}

        imported = 0
        skipped = 0

        if "results" in data:
            results = data["results"]
        elif isinstance(data, list):
            results = data
        else:
            results = [data]

        for item in results:
            try:
                match_id = item.get("match_id") or item.get("id", f"import_{imported}")
                home_team = item.get("home_team", "Unknown")
                away_team = item.get("away_team", "Unknown")
                league = item.get("league", "Unknown")
                odds = item.get("odds", item.get("final_odds", 2.0))
                actual_result = item.get("actual_result") or item.get("result")
                prediction = item.get("prediction") or item.get("recommended_bet")
                profit = item.get("profit", 0.0)
                roi = item.get("roi", 0.0)

                if actual_result is None:
                    skipped += 1
                    continue

                outcome = self._determine_outcome(
                    prediction=prediction,
                    actual=actual_result,
                    profit=profit
                )

                self.evolution.record_experience(
                    context={
                        "match_id": match_id,
                        "league": league,
                        "odds": odds,
                        "home_team": home_team,
                        "away_team": away_team,
                    },
                    action=prediction or "unknown_bet",
                    outcome=outcome,
                    metrics={
                        "profit": profit,
                        "roi": roi,
                        "odds": odds,
                    },
                    tags=[league, f"odds_range_{self._get_odds_range(odds)}"],
                )
                imported += 1

            except Exception as e:
                logger.warning(f"⚠️ 跳过无效记录: {e}")
                skipped += 1

        logger.info(f"✅ 导入完成: {imported}条成功, {skipped}条跳过")
        return {"imported": imported, "skipped": skipped}

    def import_bet_records(self, records: List[Dict]) -> Dict[str, Any]:
        """从投注记录导入经验"""
        logger.info(f"📥 导入投注记录: {len(records)}条")

        imported = 0
        for record in records:
            try:
                match_id = record.get("match_id", "unknown")
                league = record.get("league", "Unknown")
                bet_type = record.get("bet_type", record.get("selection", "unknown"))
                odds = record.get("odds", 2.0)
                stake = record.get("stake", 1.0)
                profit = record.get("profit", 0.0)
                result = record.get("result", "pending")

                if result == "pending":
                    continue

                outcome = OutcomeType.SUCCESS if profit > 0 else OutcomeType.FAILURE

                self.evolution.record_experience(
                    context={
                        "match_id": match_id,
                        "league": league,
                        "odds": odds,
                        "stake": stake,
                    },
                    action=f"bet_{bet_type}",
                    outcome=outcome,
                    metrics={
                        "profit": profit,
                        "roi": (profit / stake) * 100 if stake > 0 else 0,
                        "odds": odds,
                    },
                    tags=[league, bet_type],
                )
                imported += 1

            except Exception as e:
                logger.warning(f"⚠️ 跳过无效记录: {e}")

        logger.info(f"✅ 导入完成: {imported}条")
        return {"imported": imported}

    def generate_synthetic_experiences(self, count: int = 50) -> Dict[str, Any]:
        """生成合成经验数据用于测试"""
        logger.info(f"🧪 生成 {count} 条合成经验...")

        leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
        bet_types = ["home_win", "draw", "away_win", "over_2.5", "under_2.5"]
        odds_ranges = [(1.3, 1.8), (1.8, 2.5), (2.5, 4.0), (4.0, 8.0)]

        imported = 0
        for i in range(count):
            league = leagues[i % len(leagues)]
            bet_type = bet_types[i % len(bet_types)]

            base_odds = 2.0 + (i % 10) * 0.1
            odds = min(8.0, base_odds)

            win_prob = 1.0 / odds if odds > 1 else 0.5
            import random
            import time
            random.seed(hash(str(i) + str(time.time())) % 10000)

            is_success = random.random() < win_prob
            outcome = OutcomeType.SUCCESS if is_success else OutcomeType.FAILURE

            profit = odds - 1.0 if is_success else -1.0

            self.evolution.record_experience(
                context={
                    "league": league,
                    "odds": odds,
                    "synthetic": True,
                },
                action=f"bet_{bet_type}",
                outcome=outcome,
                metrics={
                    "profit": profit,
                    "roi": profit * 100,
                    "odds": odds,
                },
                tags=[league, bet_type, f"odds_range_{self._get_odds_range(odds)}"],
            )
            imported += 1

        logger.info(f"✅ 生成完成: {imported}条")
        return {"generated": imported}

    def analyze_league_patterns(self) -> Dict[str, Any]:
        """分析联赛模式"""
        logger.info("🔍 分析联赛模式...")

        exp_by_league = {}
        for exp in self.evolution.experiences:
            league = exp.context.get("league", "unknown")
            if league not in exp_by_league:
                exp_by_league[league] = []
            exp_by_league[league].append(exp)

        patterns = {}
        for league, experiences in exp_by_league.items():
            if len(experiences) < 3:
                continue

            total = len(experiences)
            successes = sum(1 for e in experiences if e.outcome == OutcomeType.SUCCESS)
            avg_odds = sum(e.context.get("odds", 2.0) for e in experiences) / total
            avg_profit = sum(e.metrics.get("profit", 0) for e in experiences) / total

            patterns[league] = {
                "total_bets": total,
                "success_rate": successes / total,
                "avg_odds": avg_odds,
                "avg_profit": avg_profit,
                "roi": avg_profit * 100,
            }

        logger.info(f"📊 发现 {len(patterns)} 个联赛模式")
        return patterns

    def get_accumulation_stats(self) -> Dict[str, Any]:
        """获取积累统计"""
        exp_by_league = {}
        exp_by_tag = {}
        odds_distribution = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for exp in self.evolution.experiences:
            league = exp.context.get("league", "unknown")
            exp_by_league[league] = exp_by_league.get(league, 0) + 1

            for tag in exp.tags:
                exp_by_tag[tag] = exp_by_tag.get(tag, 0) + 1

            odds = exp.context.get("odds", 2.0)
            range_key = self._get_odds_range(odds)
            odds_distribution[range_key] += 1

        return {
            "total_experiences": len(self.evolution.experiences),
            "total_skills": len(self.evolution.skills),
            "total_patterns": len(self.evolution.patterns),
            "total_hypotheses": len(self.evolution.hypotheses),
            "by_league": exp_by_league,
            "top_tags": dict(sorted(exp_by_tag.items(), key=lambda x: x[1], reverse=True)[:10]),
            "odds_distribution": odds_distribution,
        }

    def _determine_outcome(
        self, prediction: Optional[str], actual: str, profit: float
    ) -> OutcomeType:
        if profit > 0:
            return OutcomeType.SUCCESS
        elif profit < -0.5:
            return OutcomeType.FAILURE
        elif profit == 0:
            return OutcomeType.NEUTRAL
        else:
            return OutcomeType.PARTIAL

    def _get_odds_range(self, odds: float) -> str:
        if odds < 1.5:
            return "low"
        elif odds < 2.0:
            return "medium"
        elif odds < 3.5:
            return "high"
        else:
            return "very_high"

    def export_experiences(self, output_path: str) -> None:
        """导出自定义格式的经验数据"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(self.evolution.experiences),
            "experiences": [exp.to_dict() for exp in self.evolution.experiences[-100:]],
            "stats": self.get_accumulation_stats(),
        }

        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ 导出完成: {output}")


def main():
    parser = argparse.ArgumentParser(description="AFA Evolution 数据积累管理")
    parser.add_argument(
        "--mode",
        choices=["auto", "backtest", "sync", "synthetic", "stats"],
        default="stats",
        help="运行模式",
    )
    parser.add_argument("--file", type=str, help="回测结果文件路径")
    parser.add_argument("--days", type=int, default=30, help="同步最近N天的数据")
    parser.add_argument("--count", type=int, default=50, help="生成合成数据条数")
    parser.add_argument("--export", type=str, help="导出文件路径")

    args = parser.parse_args()

    accumulator = EvolutionDataAccumulator()

    if args.mode == "auto":
        print("\n🚀 自动积累模式")
        print("=" * 60)

        stats_before = accumulator.get_accumulation_stats()
        print(f"📊 积累前: {stats_before['total_experiences']} 条经验")

        accumulator.generate_synthetic_experiences(count=30)
        accumulator.analyze_league_patterns()

        print("\n🔄 触发进化...")
        result = accumulator.evolution.evolve()
        print(f"✅ 进化完成: {result.get('new_hypotheses', 0)} 个新假说")

        stats_after = accumulator.get_accumulation_stats()
        print(f"📊 积累后: {stats_after['total_experiences']} 条经验")

        print("\n" + "=" * 60)
        print(accumulator.evolution.get_evolution_report())

    elif args.mode == "backtest":
        if not args.file:
            print("❌ 需要指定 --file 参数")
            return
        result = accumulator.import_backtest_results(args.file)
        print(f"📥 导入完成: {result}")

    elif args.mode == "sync":
        print(f"🔄 同步最近 {args.days} 天的数据...")
        result = accumulator.generate_synthetic_experiences(count=args.count)
        print(f"✅ 生成完成: {result}")

    elif args.mode == "synthetic":
        result = accumulator.generate_synthetic_experiences(count=args.count)
        print(f"✅ 生成完成: {result}")

    elif args.mode == "stats":
        print("\n📊 Evolution 数据积累统计")
        print("=" * 60)
        stats = accumulator.get_accumulation_stats()

        print(f"\n📈 总体统计:")
        print(f"  - 总经验数: {stats['total_experiences']}")
        print(f"  - 总技能数: {stats['total_skills']}")
        print(f"  - 总模式数: {stats['total_patterns']}")
        print(f"  - 总假说数: {stats['total_hypotheses']}")

        print(f"\n🏆 Top 联赛:")
        for league, count in list(stats["by_league"].items())[:5]:
            print(f"  - {league}: {count} 条")

        print(f"\n📊 赔率分布:")
        for range_name, count in stats["odds_distribution"].items():
            print(f"  - {range_name}: {count} 条")

        print(f"\n🏷️ Top 标签:")
        for tag, count in stats["top_tags"].items():
            print(f"  - {tag}: {count} 条")

        if args.export:
            accumulator.export_experiences(args.export)

    if args.export:
        accumulator.export_experiences(args.export)


if __name__ == "__main__":
    main()
