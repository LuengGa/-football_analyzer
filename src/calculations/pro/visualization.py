"""
Visualization Module - 可视化模块
提供结果图表、回测可视化、预测分析等功能
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class SimpleVisualizer:
    """简单可视化器 - 不依赖外部库的 ASCII/文本可视化"""

    @staticmethod
    def print_probability_bar(probability: float, label: str, width: int = 50) -> str:
        """打印概率条形图"""
        filled = int(probability * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"{label:10} |{bar}| {probability:.1%}"

    @staticmethod
    def print_prediction_comparison(home_team: str, away_team: str,
                                    home_prob: float, draw_prob: float,
                                    away_prob: float):
        """打印预测对比"""
        print(f"\n📊 预测: {home_team} vs {away_team}")
        print("-" * 70)
        print(SimpleVisualizer.print_probability_bar(home_prob, "主胜"))
        print(SimpleVisualizer.print_probability_bar(draw_prob, "平局"))
        print(SimpleVisualizer.print_probability_bar(away_prob, "客胜"))
        print("-" * 70)

    @staticmethod
    def print_value_bet_table(bets: List[Dict]):
        """打印价值投注表格"""
        print("\n" + "=" * 100)
        print(f"{'比赛':40} | {'类型':8} | {'赔率':6} | {'优势':8} | {'期望':8} | {'信心':8}")
        print("=" * 100)

        for bet in bets[:10]:
            match_str = f"{bet.get('home_team', 'N/A')[:18]} vs {bet.get('away_team', 'N/A')[:18]}"
            bet_type = bet.get('bet_type', 'N/A')
            if hasattr(bet_type, 'value'):
                bet_type = bet_type.value
            odds = bet.get('odds', 0.0)
            edge = bet.get('edge', 0.0)
            ev = bet.get('expected_value', 0.0)
            conf = bet.get('confidence', 0.0)

            print(f"{match_str:40} | {bet_type:8} | {odds:6.2f} | {edge:8.2%} | {ev:8.3f} | {conf:8.1%}")

        if len(bets) > 10:
            print(f"\n... 还有 {len(bets) - 10} 个投注机会")

    @staticmethod
    def print_backtest_chart(returns_history: List[float], initial_capital: float = 10000):
        """打印回测资金曲线 (ASCII 图表)"""
        if not returns_history:
            return

        print("\n📈 资金曲线 (ASCII 图表)")
        print("-" * 80)

        history = returns_history
        min_val = min(history) if history else 0
        max_val = max(history) if history else initial_capital * 2
        height = 20

        chart_lines = []
        for row in range(height, -1, -1):
            line = []
            val = min_val + (max_val - min_val) * (row / height)
            for point in history[::max(1, len(history) // 60)]:
                if point >= val:
                    line.append('█')
                else:
                    line.append(' ')
            chart_lines.append(''.join(line))

        for line in chart_lines:
            print('  ' + line)

        print(f"\n  初始资金: ¥{initial_capital:,.2f}")
        print(f"  最终资金: ¥{history[-1]:,.2f}")
        print(f"  总收益: ¥{history[-1] - initial_capital:,.2f} ({((history[-1] - initial_capital) / initial_capital):.1%})")

    @staticmethod
    def print_htft_prediction(htft_result):
        """打印 HT/FT 预测表格"""
        print("\n🏟️  半场/全场预测 (HT/FT)")
        print("-" * 60)

        print("          半场 ↓ / 全场 → | 主胜    平局    客胜")
        print("-" * 60)

        hh = getattr(htft_result, 'home_home', 0.0)
        hd = getattr(htft_result, 'home_draw', 0.0)
        ha = getattr(htft_result, 'home_away', 0.0)
        print(f"  主胜                | {hh:6.1%}  {hd:6.1%}  {ha:6.1%}")

        dh = getattr(htft_result, 'draw_home', 0.0)
        dd = getattr(htft_result, 'draw_draw', 0.0)
        da = getattr(htft_result, 'draw_away', 0.0)
        print(f"  平局                | {dh:6.1%}  {dd:6.1%}  {da:6.1%}")

        ah = getattr(htft_result, 'away_home', 0.0)
        ad = getattr(htft_result, 'away_draw', 0.0)
        aa = getattr(htft_result, 'away_away', 0.0)
        print(f"  客胜                | {ah:6.1%}  {ad:6.1%}  {aa:6.1%}")

        if hasattr(htft_result, 'most_likely'):
            print(f"\n🎯 最可能结果: {htft_result.most_likely}")

    @staticmethod
    def print_live_prediction_simulation(home_team: str, away_team: str, updates: List[Any]):
        """打印实时预测模拟"""
        print(f"\n⚽ 实时预测模拟: {home_team} vs {away_team}")
        print("-" * 80)
        print(f"{'分钟':6} | {'比分':10} | {'主胜':8} | {'平局':8} | {'客胜':8} | {'大2.5':8}")
        print("-" * 80)

        for update in updates:
            minute = getattr(update, 'minute', 0)
            hg = getattr(update, 'home_goals', 0)
            ag = getattr(update, 'away_goals', 0)
            hp = getattr(update, 'home_win_prob', 0.0)
            dp = getattr(update, 'draw_prob', 0.0)
            ap = getattr(update, 'away_win_prob', 0.0)
            o25 = getattr(update, 'over_2_5_prob', 0.0)

            print(f"{minute:6} | {hg}-{ag:8} | {hp:8.1%} | {dp:8.1%} | {ap:8.1%} | {o25:8.1%}")


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_system_summary(self, orchestrator, filename: str = "system_summary.json"):
        """生成系统摘要报告"""
        status = orchestrator.get_system_status() if hasattr(orchestrator, 'get_system_status') else {}

        summary = {
            'generated_at': str(__import__('datetime').datetime.now()),
            'system_status': status,
            'matches_loaded': getattr(orchestrator, 'matches_loaded', 0)
        }

        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n📄 系统摘要已保存至: {filepath}")
        return filepath

    def generate_backtest_report(self, backtest_result, filename: str = "backtest_report.json"):
        """生成回测报告"""
        report = {
            'generated_at': str(__import__('datetime').datetime.now()),
            'strategy': getattr(backtest_result, 'strategy_name', 'unknown'),
            'total_bets': getattr(backtest_result, 'total_bets', 0),
            'win_rate': getattr(backtest_result, 'win_rate', 0.0),
            'roi': getattr(backtest_result, 'roi', 0.0),
            'max_drawdown': getattr(backtest_result, 'max_drawdown', 0.0),
            'sharpe_ratio': getattr(backtest_result, 'sharpe_ratio', 0.0)
        }

        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath
