"""
Walk-Forward Validation - 滚动验证系统
实现：
1. 时间窗口分割
2. 滚动训练与测试
3. 联赛特定模型
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .poisson_model import PoissonGoalModel
from .strategy_backtest import StrategyTester, StrategyResult


@dataclass
class WalkForwardResult:
    """滚动验证结果"""
    windows_tested: int
    total_bets: int
    average_roi: float
    sharpe_ratio: float
    max_drawdown: float
    consistent_windows: int
    league_results: Dict[str, Dict]


class WalkForwardValidator:
    """滚动验证引擎"""
    
    def __init__(
        self,
        training_window_months: int = 12,
        testing_window_months: int = 1,
        step_months: int = 1
    ):
        self.training_window = training_window_months
        self.testing_window = testing_window_months
        self.step = step_months
        
    def _split_by_date(self, matches: List) -> List[Tuple[List, List]]:
        """按时间顺序分割训练和测试窗口"""
        # 按日期排序
        sorted_matches = sorted(
            matches,
            key=lambda m: getattr(m, 'date', '0')
        )
        
        if not sorted_matches:
            return []
            
        # 简化版分割（实际项目中需要解析日期）
        # 这里我们用等分为N个窗口
        n = len(sorted_matches)
        window_size = max(100, n // 10)
        
        windows = []
        for i in range(0, n - window_size, window_size // 2):
            train_matches = sorted_matches[:i + window_size]
            test_matches = sorted_matches[i + window_size:i + window_size + window_size // 2]
            
            if len(test_matches) > 0:
                windows.append((train_matches, test_matches))
                
        return windows
        
    def validate_strategy(
        self,
        matches: List,
        strategy_name: str,
        use_league_specific: bool = False
    ) -> WalkForwardResult:
        """
        完整滚动验证
        """
        print("\n" + "="*80)
        print("📊 Walk-Forward Validation")
        print("="*80)
        
        windows = self._split_by_date(matches)
        print(f"\n📅 Testing {len(windows)} windows...")
        
        all_results = []
        window_idx = 1
        
        for train_matches, test_matches in windows:
            print(f"\n--- Window {window_idx}/{len(windows)} ---")
            print(f"  Training: {len(train_matches)} matches")
            print(f"  Testing: {len(test_matches)} matches")
            
            # 训练模型
            if use_league_specific:
                # 按联赛分别训练
                league_models = {}
                league_matches = defaultdict(list)
                
                for m in train_matches:
                    league = getattr(m, 'league_name', 'unknown')
                    league_matches[league].append(m)
                
                for league, matches_list in league_matches.items():
                    if len(matches_list) >= 50:
                        model = PoissonGoalModel()
                        model.fit(matches_list)
                        league_models[league] = model
                
                # 分别测试
                for league, model in league_models.items():
                    league_test = [m for m in test_matches if getattr(m, 'league_name', '') == league]
                    
                    if league_test:
                        tester = StrategyTester()
                        result = tester.backtest_strategy(
                            strategy_name, league_test, model
                        )
                        all_results.append(result)
            else:
                # 全局模型
                model = PoissonGoalModel()
                model.fit(train_matches)
                
                # 测试
                tester = StrategyTester()
                result = tester.backtest_strategy(strategy_name, test_matches, model)
                all_results.append(result)
                
            window_idx += 1
            
        # 汇总结果
        total_bets = sum(r.total_bets for r in all_results)
        average_roi = sum(r.roi for r in all_results) / len(all_results) if all_results else 0
        positive_windows = sum(1 for r in all_results if r.net_profit > 0)
        
        # 计算夏普
        all_returns = []
        for r in all_results:
            if r.bets:
                for bet in r.bets:
                    all_returns.append(bet.profit)
        
        if all_returns:
            import numpy as np
            avg_return = np.mean(all_returns)
            std_return = np.std(all_returns)
            sharpe = (avg_return / std_return) * np.sqrt(52) if std_return > 0 else 0
        else:
            sharpe = 0
            
        # 最大回撤
        max_dd = max(r.max_drawdown for r in all_results)
        
        print("\n" + "="*80)
        print("📊 Walk-Forward Results")
        print("="*80)
        print(f"  Windows: {len(windows)}")
        print(f"  Positive: {positive_windows}/{len(windows)} ({positive_windows/len(windows)*100:.1f}%)")
        print(f"  Total Bets: {total_bets}")
        print(f"  Avg ROI: {average_roi:.2f}%")
        print(f"  Sharpe: {sharpe:.2f}")
        
        return WalkForwardResult(
            windows_tested=len(windows),
            total_bets=total_bets,
            average_roi=average_roi,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            consistent_windows=positive_windows,
            league_results={}
        )


class LeagueSpecificTrainer:
    """联赛特定模型训练器"""
    
    def __init__(self):
        self.league_models: Dict[str, PoissonGoalModel] = {}
        
    def train_all_leagues(self, matches: List, min_matches: int = 100) -> Dict[str, PoissonGoalModel]:
        """训练所有联赛的特定模型"""
        from collections import defaultdict
        
        league_matches = defaultdict(list)
        for match in matches:
            league = getattr(match, 'league_name', 'unknown')
            league_matches[league].append(match)
            
        print(f"\n📊 Training league-specific models: {len(league_matches)} leagues")
        
        for league, matches_list in league_matches.items():
            if len(matches_list) >= min_matches:
                print(f"  Training: {league} ({len(matches_list)} matches)")
                model = PoissonGoalModel()
                model.fit(matches_list)
                self.league_models[league] = model
                
        print(f"\n✅ Trained {len(self.league_models)} league models")
        
        return self.league_models
        
    def get_model(self, league: str) -> Optional[PoissonGoalModel]:
        """获取特定联赛的模型"""
        return self.league_models.get(league)
