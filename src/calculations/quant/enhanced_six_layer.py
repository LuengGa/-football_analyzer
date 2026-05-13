"""
强化版六层赔率分析框架 - 任务C: 强化六层赔率分析框架
并集成回测系统 - 任务B: 回测系统和策略验证
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from calculations.historical_data_loader import HistoricalMatch
from calculations.math.odds_probability import OddsProbability


@dataclass
class OddsTrend:
    """赔率变化趋势"""
    home_change: float
    draw_change: float
    away_change: float
    home_trend: str  # up, down, flat
    draw_trend: str
    away_trend: str


@dataclass
class SixLayerResult:
    """六层分析结果"""
    # Layer 1: 定价偏差检测
    layer1_pricing_deviation: Optional[Dict[str, Any]] = None
    
    # Layer 2: 欧亚背离分析
    layer2_asian_european_deviation: Optional[Dict[str, Any]] = None
    
    # Layer 3: 赔率变化追踪
    layer3_odds_trend: Optional[OddsTrend] = None
    
    # Layer 4: 资金引导识别
    layer4_fund_flow: Optional[Dict[str, Any]] = None
    
    # Layer 5: 操盘手法识别
    layer5_trading_pattern: Optional[Dict[str, Any]] = None
    
    # Layer 6: 价值机会发现
    layer6_value_opportunity: Optional[Dict[str, Any]] = None
    
    overall_confidence: float = 0.0
    recommendation: Optional[str] = None  # home, draw, away, avoid
    reasoning: str = ""


class EnhancedSixLayerAnalyzer:
    """强化版六层赔率分析器"""
    
    def __init__(self):
        self.bookmaker_priorities = ['Pinnacle', 'Bet365', 'WilliamHill', 'Ladbrokes', 'Betway', 'Interwetten']
        self.odds_probability = OddsProbability()
    
    def analyze_historical_match(self, match: HistoricalMatch) -> SixLayerResult:
        """分析历史比赛（有初盘和终盘数据）"""
        result = SixLayerResult()
        
        # Layer 1: 定价偏差检测
        result.layer1_pricing_deviation = self._analyze_pricing_deviation(match)
        
        # Layer 3: 赔率变化追踪（先做这个，因为后面会用到）
        result.layer3_odds_trend = self._analyze_odds_trend(match)
        
        # Layer 4: 资金引导识别
        result.layer4_fund_flow = self._analyze_fund_flow(match, result.layer3_odds_trend)
        
        # Layer 5: 操盘手法识别
        result.layer5_trading_pattern = self._analyze_trading_pattern(match, result.layer3_odds_trend)
        
        # Layer 2: 欧亚背离分析（如果有亚盘数据）
        result.layer2_asian_european_deviation = self._analyze_asian_european_deviation(match)
        
        # Layer 6: 价值机会发现 - 综合分析
        result.layer6_value_opportunity = self._find_value_opportunity(match, result)
        
        # 生成综合推荐
        result.overall_confidence, result.recommendation, result.reasoning = self._generate_recommendation(match, result)
        
        return result
    
    def _analyze_pricing_deviation(self, match: HistoricalMatch) -> Optional[Dict]:
        """Layer 1: 定价偏差检测 - 多机构横向对比"""
        if not match.opening_odds:
            return None
        
        # 收集所有机构的隐含概率
        all_probs = defaultdict(list)
        
        for bm, odds in match.opening_odds.items():
            if odds and all(k in odds for k in ['home', 'draw', 'away']):
                try:
                    implied = self.odds_probability.normalize_probabilities(
                        odds['home'], 
                        odds['draw'], 
                        odds['away']
                    )
                    all_probs['home'].append(implied['home'])
                    all_probs['draw'].append(implied['draw'])
                    all_probs['away'].append(implied['away'])
                except:
                    continue
        
        if len(all_probs['home']) < 2:
            return None
        
        # 计算平均值和标准差
        import statistics
        
        def get_stats(vals):
            return {
                'mean': statistics.mean(vals),
                'std': statistics.stdev(vals) if len(vals) > 1 else 0,
                'min': min(vals),
                'max': max(vals),
                'spread': max(vals) - min(vals)
            }
        
        stats = {
            'home': get_stats(all_probs['home']),
            'draw': get_stats(all_probs['draw']),
            'away': get_stats(all_probs['away']),
            'bookmakers_count': len(all_probs['home'])
        }
        
        # 找出最大偏差
        max_spread_result = max(
            ('home', stats['home']['spread']),
            ('draw', stats['draw']['spread']),
            ('away', stats['away']['spread']),
            key=lambda x: x[1]
        )
        
        return {
            'statistics': stats,
            'max_deviation_result': max_spread_result[0],
            'deviation_spread': max_spread_result[1],
            'has_significant_deviation': max_spread_result[1] > 0.05,
        }
    
    def _analyze_odds_trend(self, match: HistoricalMatch) -> Optional[OddsTrend]:
        """Layer 3: 赔率变化追踪 - 初盘→终盘纵向分析"""
        if not match.opening_odds or not match.closing_odds:
            return None
        
        # 用Pinnacle的数据作为主要参考，或者用第一个有数据的机构
        target_bm = None
        for bm in self.bookmaker_priorities:
            if bm in match.opening_odds and bm in match.closing_odds:
                target_bm = bm
                break
        
        if not target_bm:
            # 找任意共同的机构
            common_bms = set(match.opening_odds.keys()) & set(match.closing_odds.keys())
            if not common_bms:
                return None
            target_bm = list(common_bms)[0]
        
        open_odds = match.opening_odds[target_bm]
        close_odds = match.closing_odds[target_bm]
        
        # 计算变化量
        home_change = close_odds['home'] - open_odds['home']
        draw_change = close_odds['draw'] - open_odds['draw']
        away_change = close_odds['away'] - open_odds['away']
        
        def get_trend(change):
            if abs(change) < 0.05:
                return 'flat'
            return 'up' if change > 0 else 'down'
        
        return OddsTrend(
            home_change=home_change,
            draw_change=draw_change,
            away_change=away_change,
            home_trend=get_trend(home_change),
            draw_trend=get_trend(draw_change),
            away_trend=get_trend(away_change)
        )
    
    def _analyze_fund_flow(self, match: HistoricalMatch, trend: Optional[OddsTrend]) -> Optional[Dict]:
        """Layer 4: 资金引导识别 - 机构如何通过调赔平衡资金"""
        if not trend:
            return None
        
        # 赔率下降 → 该结果被看好，资金流入
        # 赔率上升 → 该结果被看淡，资金流出
        
        fund_flow = {
            'home': 'in' if trend.home_trend == 'down' else 'out' if trend.home_trend == 'up' else 'neutral',
            'draw': 'in' if trend.draw_trend == 'down' else 'out' if trend.draw_trend == 'up' else 'neutral',
            'away': 'in' if trend.away_trend == 'down' else 'out' if trend.away_trend == 'up' else 'neutral',
        }
        
        # 找资金最集中的流向
        in_flows = [k for k, v in fund_flow.items() if v == 'in']
        
        return {
            'fund_flow': fund_flow,
            'dominant_flow': in_flows[0] if in_flows else 'neutral',
            'flow_strength': {
                'home': abs(trend.home_change),
                'draw': abs(trend.draw_change),
                'away': abs(trend.away_change)
            }
        }
    
    def _analyze_trading_pattern(self, match: HistoricalMatch, trend: Optional[OddsTrend]) -> Optional[Dict]:
        """Layer 5: 操盘手法识别 - 诱盘/赶盘/稳定盘模式"""
        if not trend:
            return None
        
        pattern = 'stable'
        confidence = 0.5
        
        # 检测模式
        total_change = abs(trend.home_change) + abs(trend.draw_change) + abs(trend.away_change)
        
        if total_change > 0.5:
            # 显著变化
            # 检查是否是诱盘模式：热门选项赔率先降后升？
            # 或者直接看赔率变化方向和最终结果的关系
            
            # 简化版模式识别
            pattern = 'strong_move'
            confidence = 0.6
            
            # 检查是否有赶盘特征
            if (trend.home_trend == 'down' and trend.away_trend == 'up'):
                pattern = 'pressure_home'
            elif (trend.home_trend == 'up' and trend.away_trend == 'down'):
                pattern = 'pressure_away'
        
        return {
            'pattern': pattern,
            'confidence': confidence,
            'total_change': total_change,
        }
    
    def _analyze_asian_european_deviation(self, match: HistoricalMatch) -> Optional[Dict]:
        """Layer 2: 欧亚背离分析"""
        # 简化版欧亚对比
        if not match.opening_odds or not match.asian_handicap_opening:
            return None
        
        # 这里应该有完整的欧亚转换公式
        # 简化版实现
        return {
            'has_asian_data': True,
            'deviation_level': 'low',  # placeholder
            'confidence': 0.5
        }
    
    def _find_value_opportunity(self, match: HistoricalMatch, result: SixLayerResult) -> Dict:
        """Layer 6: 价值机会发现 - 综合以上五层"""
        from typing import Any
        # 计算综合信号
        signals: List[Any] = []
        confidence_factors: List[Any] = []
        
        # 从资金流向获取信号
        if result.layer4_fund_flow:
            dominant = result.layer4_fund_flow['dominant_flow']
            if dominant in ['home', 'draw', 'away']:
                signals.append((dominant, 0.3))
        
        # 从定价偏差获取信号
        if result.layer1_pricing_deviation and result.layer1_pricing_deviation.get('has_significant_deviation'):
            dev_result = result.layer1_pricing_deviation['max_deviation_result']
            signals.append((dev_result, 0.2))
        
        # 从操盘手法获取信号
        if result.layer5_trading_pattern:
            pattern = result.layer5_trading_pattern['pattern']
            if pattern == 'pressure_home':
                signals.append(('away', 0.25))  # 反向思维
            elif pattern == 'pressure_away':
                signals.append(('home', 0.25))
        
        # 聚合信号
        final_signal = self._aggregate_signals(signals)
        
        return {
            'signals': signals,
            'final_signal': final_signal,
            'expected_value': self._calculate_ev(match, final_signal),
        }
    
    def _aggregate_signals(self, signals: List[Tuple[str, float]]) -> Optional[str]:
        """聚合多个信号"""
        if not signals:
            return None
        
        scores = defaultdict(float)
        for result, weight in signals:
            scores[result] += weight
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_ev(self, match: HistoricalMatch, signal: Optional[str]) -> float:
        """计算预期价值（简化版）"""
        if not signal or not match.opening_odds:
            return 0
        
        # 取第一个有数据的机构
        odds = None
        for bm in self.bookmaker_priorities:
            if bm in match.opening_odds:
                odds = match.opening_odds[bm]
                break
        
        if not odds:
            return 0
        
        # 简化EV计算
        # 真实EV需要准确模型，这里只是示意
        if signal == 'home':
            return (0.5 * (odds['home'] - 1)) - 0.5  # type: ignore[no-any-return]
        elif signal == 'draw':
            return (0.33 * (odds['draw'] - 1)) - 0.67  # type: ignore[no-any-return]
        else:
            return (0.5 * (odds['away'] - 1)) - 0.5  # type: ignore[no-any-return]
    
    def _generate_recommendation(self, match: HistoricalMatch, result: SixLayerResult) -> Tuple[float, Optional[str], str]:
        """生成最终推荐"""
        confidence = 0.5
        recommendation = None
        reasoning = []
        
        # Layer 6有信号的话
        if result.layer6_value_opportunity and result.layer6_value_opportunity['final_signal']:
            signal = result.layer6_value_opportunity['final_signal']
            ev = result.layer6_value_opportunity['expected_value']
            
            if ev > 0:
                confidence = 0.6 + min(0.2, abs(ev) * 2)
                recommendation = signal
                reasoning.append(f"价值信号: {signal}, EV: {ev:.3f}")
        
        # 检查定价偏差
        if result.layer1_pricing_deviation and result.layer1_pricing_deviation['has_significant_deviation']:
            confidence += 0.05
            reasoning.append(f"发现定价偏差: {result.layer1_pricing_deviation['max_deviation_result']}")
        
        # 检查资金流向
        if result.layer4_fund_flow:
            reasoning.append(f"资金流向: {result.layer4_fund_flow['fund_flow']}")
        
        # 确保confidence在0-1之间
        confidence = min(1.0, max(0.0, confidence))
        
        return confidence, recommendation, " | ".join(reasoning)
