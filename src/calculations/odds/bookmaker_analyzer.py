"""
BookmakerAnalyzer - 庄家意图与市场对比分析器（整合六层框架）
核心功能：欧指、亚盘、竞彩、北单 四个市场对比分析
集成六层赔率分析框架，用于发现定价偏差和价值机会
"""
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from .six_layer_analyzer import (
    get_six_layer_analyzer,
    AsianHandicap,
    Layer6ValueOpportunityEngine
)


@dataclass
class MarketOdds:
    """市场赔率数据"""
    market: str  # eu, asian, jingcai, beidan
    home_odds: float
    away_odds: float
    draw_odds: float = None
    handicap: float = None
    water: float = None
    timestamp: datetime = None
    source: str = None


class MarketComparator:
    """市场对比器 - 核心功能：四个市场对比"""
    
    RETURN_RATES = {
        "eu": 0.93,
        "asian": 0.90,
        "jingcai": 0.69,
        "beidan": 0.65
    }
    
    def __init__(self):
        self.markets_data = {}
    
    def add_market_data(self, market: str, odds_data: Dict[str, float]):
        """添加市场数据"""
        self.markets_data[market] = {
            "home": odds_data.get("home"),
            "draw": odds_data.get("draw"),
            "away": odds_data.get("away"),
            "handicap": odds_data.get("handicap"),
            "timestamp": datetime.now()
        }
    
    def convert_to_probability(self, odds: float, market: str) -> float:
        """将赔率转换为隐含概率"""
        if odds <= 0:
            return 0.0
        return_rate = self.RETURN_RATES.get(market, 0.90)
        return (1.0 / odds) * return_rate
    
    def compare_markets(self) -> Dict[str, Any]:
        """对比所有市场"""
        if len(self.markets_data) < 2:
            return {"error": "需要至少2个市场数据"}
        
        results = {
            "comparisons": [],
            "pricing_errors": [],
            "opportunities": []
        }
        
        market_probs = {}
        for market, data in self.markets_data.items():
            if data.get("home"):
                market_probs[market] = {
                    "home": self.convert_to_probability(data["home"], market),
                    "away": self.convert_to_probability(data["away"], market)
                }
        
        markets = list(market_probs.keys())
        for i, m1 in enumerate(markets):
            for m2 in markets[i+1:]:
                prob1 = market_probs[m1]
                prob2 = market_probs[m2]
                
                home_diff = abs(prob1["home"] - prob2["home"])
                away_diff = abs(prob1["away"] - prob2["away"])
                
                comparison = {
                    "market_pair": f"{m1} vs {m2}",
                    "home_diff_pct": round(home_diff * 100, 2),
                    "away_diff_pct": round(away_diff * 100, 2),
                    "total_diff": round((home_diff + away_diff) * 100, 2)
                }
                results["comparisons"].append(comparison)
                
                if home_diff > 0.05:
                    results["pricing_errors"].append({
                        "type": "home_pricing_error",
                        "markets": f"{m1} vs {m2}",
                        "diff": round(home_diff * 100, 2),
                        "direction": m1 if prob1["home"] > prob2["home"] else m2
                    })
        
        if results["pricing_errors"]:
            results["opportunities"] = self._find_opportunities(market_probs)
        
        return results
    
    def _find_opportunities(self, market_probs: Dict) -> List[Dict]:
        """发现价值机会"""
        opportunities = []
        
        for outcome in ["home", "away"]:
            probs = {m: data[outcome] for m, data in market_probs.items()}
            min_market = min(probs, key=probs.get)
            max_market = max(probs, key=probs.get)
            
            diff = probs[max_market] - probs[min_market]
            if diff > 0.03:
                opportunities.append({
                    "outcome": outcome,
                    "best_market": min_market,
                    "worst_market": max_market,
                    "value_pct": round(diff * 100, 2),
                    "recommendation": f"买{min_market}的{outcome}"
                })
        
        return opportunities


class FundFlowAnalyzer:
    """资金流向分析器"""
    
    def __init__(self):
        self.odds_history = []
    
    def add_odds_snapshot(self, market: str, odds: Dict[str, float], timestamp: datetime = None):
        """添加赔率快照"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.odds_history.append({
            "market": market,
            "odds": odds,
            "timestamp": timestamp
        })
    
    def analyze_trend(self, market: str) -> Dict[str, Any]:
        """分析趋势"""
        market_history = [h for h in self.odds_history if h["market"] == market]
        
        if len(market_history) < 2:
            return {"trend": "insufficient_data"}
        
        market_history.sort(key=lambda x: x["timestamp"])
        
        first = market_history[0]["odds"]["home"]
        last = market_history[-1]["odds"]["home"]
        change_pct = ((last - first) / first) * 100
        
        return {
            "trend": "increasing" if change_pct > 2 else "decreasing" if change_pct < -2 else "stable",
            "change_pct": round(change_pct, 2),
            "snapshots": len(market_history)
        }
    
    def detect_fund_flow(self, market: str) -> Dict[str, Any]:
        """检测资金流向"""
        trend = self.analyze_trend(market)
        
        if trend["trend"] == "insufficient_data":
            return {"fund_flow": "unknown"}
        
        if trend["trend"] == "decreasing":
            return {
                "fund_flow": "inflow",
                "interpretation": "市场资金涌入该选项",
                "change_pct": trend["change_pct"]
            }
        elif trend["trend"] == "increasing":
            return {
                "fund_flow": "outflow",
                "interpretation": "市场资金撤离该选项",
                "change_pct": trend["change_pct"]
            }
        else:
            return {
                "fund_flow": "balanced",
                "interpretation": "资金相对平衡",
                "change_pct": trend["change_pct"]
            }


class BookmakerIntentAnalyzer:
    """庄家意图分析器（整合六层分析框架）"""
    
    def __init__(self):
        self.comparator = MarketComparator()
        self.fund_analyzer = FundFlowAnalyzer()
        self.six_layer_analyzer: Layer6ValueOpportunityEngine = get_six_layer_analyzer()
    
    def analyze(
        self,
        eu_odds: Dict[str, float] = None,
        asian_handicap: float = None,
        asian_odds: Dict[str, float] = None,
        jingcai_odds: Dict[str, float] = None,
        beidan_sp: Dict[str, float] = None,
        odds_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        全面分析（整合六层框架）
        
        Args:
            eu_odds: 欧指赔率 {"home": x, "draw": x, "away": x}
            asian_handicap: 亚盘盘口
            asian_odds: 亚盘赔率 {"home": x, "away": x}
            jingcai_odds: 竞彩赔率 {"home": x, "draw": x, "away": x}
            beidan_sp: 北单SP值 {"home": x, "draw": x, "away": x}
            odds_history: 赔率历史数据
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "markets_analyzed": [],
            "market_comparison": {},
            "fund_flows": {},
            "pricing_errors": [],
            "opportunities": [],
            "intents": {},
            "six_layer_analysis": {}
        }
        
        bookmaker_data = []
        if eu_odds:
            bookmaker_data.append({"bookmaker": "欧洲平均", "odds": eu_odds})
        if jingcai_odds:
            bookmaker_data.append({"bookmaker": "竞彩官方", "odds": jingcai_odds})
        if beidan_sp:
            bookmaker_data.append({"bookmaker": "北单", "odds": beidan_sp})
        if asian_odds:
            bookmaker_data.append({"bookmaker": "亚盘", "odds": {"home": asian_odds.get("home"), "draw": 3.5, "away": asian_odds.get("away")}})
        
        asian_handicap_obj = None
        if asian_handicap and asian_odds:
            asian_handicap_obj = AsianHandicap(
                handicap=asian_handicap,
                home_odds=asian_odds.get("home", 1.95),
                away_odds=asian_odds.get("away", 1.90)
            )
        
        primary_eu_odds = eu_odds if eu_odds else {"home": 2.0, "draw": 3.5, "away": 3.5}
        
        self.six_layer_analyzer.set_data(
            bookmaker_data=bookmaker_data,
            european_odds=primary_eu_odds,
            asian_handicap=asian_handicap_obj or AsianHandicap(handicap=0.0, home_odds=1.95, away_odds=1.95),
            odds_history=odds_history
        )
        
        six_layer_result = self.six_layer_analyzer.analyze()
        result["six_layer_analysis"] = six_layer_result
        
        if eu_odds:
            self.comparator.add_market_data("eu", eu_odds)
            result["markets_analyzed"].append("eu")
            self.fund_analyzer.add_odds_snapshot("eu", eu_odds)
            result["fund_flows"]["eu"] = self.fund_analyzer.detect_fund_flow("eu")
        
        if jingcai_odds:
            self.comparator.add_market_data("jingcai", jingcai_odds)
            result["markets_analyzed"].append("jingcai")
        
        if beidan_sp:
            self.comparator.add_market_data("beidan", beidan_sp)
            result["markets_analyzed"].append("beidan")
        
        if asian_odds:
            self.comparator.add_market_data("asian", asian_odds)
            result["markets_analyzed"].append("asian")
        
        if len(result["markets_analyzed"]) >= 2:
            comparison = self.comparator.compare_markets()
            result["market_comparison"] = comparison["comparisons"]
            result["pricing_errors"] = comparison["pricing_errors"]
            result["opportunities"] = comparison["opportunities"]
        
        result["intents"] = self._analyze_intent(
            result["fund_flows"],
            result["pricing_errors"],
            asian_handicap,
            six_layer_result.get("layer5", {})
        )
        
        result["six_layer_opportunities"] = six_layer_result.get("layer6", {}).get("opportunities", [])
        result["overall_recommendation"] = six_layer_result.get("layer6", {}).get("recommendation", "无明确建议")
        result["overall_confidence"] = six_layer_result.get("layer6", {}).get("overall_confidence", 0.3)
        
        return result
    
    def _analyze_intent(
        self,
        fund_flows: Dict,
        pricing_errors: List,
        handicap: float,
        layer5_result: Dict
    ) -> Dict[str, Any]:
        """分析庄家意图"""
        intents = {}
        
        for market, flow in fund_flows.items():
            if flow["fund_flow"] == "inflow":
                intents[market] = "资金涌入 - 可能被看好"
            elif flow["fund_flow"] == "outflow":
                intents[market] = "资金撤离 - 可能不被看好"
            else:
                intents[market] = "资金平衡 - 观望"
        
        if pricing_errors:
            intents["pricing_error_detected"] = True
            intents["error_details"] = pricing_errors
        else:
            intents["pricing_error_detected"] = False
        
        if layer5_result.get("primary_pattern"):
            pattern = layer5_result["primary_pattern"]
            intents["trading_pattern"] = {
                "name": pattern.get("name"),
                "confidence": pattern.get("confidence"),
                "analysis": layer5_result.get("analysis")
            }
        
        return intents
    
    def generate_report(self, analysis_result: Dict) -> str:
        """生成分析报告"""
        lines = ["=" * 70]
        lines.append("🎯 四市场对比分析报告（六层框架整合版）")
        lines.append("=" * 70)
        
        lines.append(f"\n分析时间: {analysis_result['timestamp']}")
        lines.append(f"分析市场: {', '.join(analysis_result['markets_analyzed'])}")
        lines.append(f"总体信心: {analysis_result.get('overall_confidence', 0.3):.1%}")
        
        lines.append("\n" + "-" * 70)
        lines.append("📊 六层分析结果:")
        lines.append("-" * 70)
        
        layer6 = analysis_result.get("six_layer_analysis", {}).get("layer6", {})
        opportunities = layer6.get("opportunities", [])
        
        if opportunities:
            lines.append("\n💎 发现的价值机会:")
            for i, opp in enumerate(opportunities[:3], 1):
                lines.append(f"  {i}. [{opp.type}] {opp.recommendation}")
                lines.append(f"     期望值: {opp.expected_value:.2f}, 信心: {opp.confidence:.1%}")
        else:
            lines.append("\n💎 未发现明显价值机会")
        
        layer5 = analysis_result.get("six_layer_analysis", {}).get("layer5", {})
        if layer5.get("primary_pattern"):
            lines.append(f"\n🎭 操盘手法识别: {layer5['primary_pattern']['name']}")
            lines.append(f"   分析: {layer5.get('analysis', '')}")
        
        lines.append("\n" + "-" * 70)
        lines.append("💰 资金流向分析:")
        lines.append("-" * 70)
        for market, flow in analysis_result.get("fund_flows", {}).items():
            lines.append(f"  {market}: {flow.get('fund_flow', 'unknown')}")
        
        if analysis_result.get("pricing_errors"):
            lines.append("\n⚠️ 定价偏差:")
            for error in analysis_result["pricing_errors"][:3]:
                lines.append(f"  {error['type']}: {error['markets']} 差异{error['diff']:.2f}%")
        
        lines.append("\n" + "-" * 70)
        lines.append(f"📌 最终建议: {analysis_result.get('overall_recommendation', '无明确建议')}")
        lines.append("=" * 70)
        
        return "\n".join(lines)


_analyzer = None

def get_bookmaker_analyzer() -> BookmakerIntentAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = BookmakerIntentAnalyzer()
    return _analyzer


if __name__ == "__main__":
    print("=" * 70)
    print("🎯 庄家意图与市场对比分析器（整合六层框架）")
    print("=" * 70)
    
    analyzer = get_bookmaker_analyzer()
    
    eu_odds = {"home": 1.85, "draw": 3.50, "away": 4.20}
    jingcai_odds = {"home": 1.55, "draw": 3.30, "away": 5.20}
    beidan_sp = {"home": 1.80, "draw": 3.60, "away": 4.50}
    asian_odds = {"home": 1.95, "away": 2.00}
    asian_handicap = -0.5
    
    odds_history = [
        {"odds": {"home": 2.00, "draw": 3.40, "away": 3.80}},
        {"odds": {"home": 1.95, "draw": 3.45, "away": 3.90}},
        {"odds": {"home": 1.90, "draw": 3.50, "away": 4.00}},
        {"odds": {"home": 1.85, "draw": 3.50, "away": 4.20}}
    ]
    
    print("\n📊 测试数据:")
    print(f"  欧指: {eu_odds}")
    print(f"  竞彩: {jingcai_odds}")
    print(f"  北单: {beidan_sp}")
    print(f"  亚盘: {asian_odds} (盘口{asian_handicap})")
    
    result = analyzer.analyze(
        eu_odds=eu_odds,
        jingcai_odds=jingcai_odds,
        beidan_sp=beidan_sp,
        asian_odds=asian_odds,
        asian_handicap=asian_handicap,
        odds_history=odds_history
    )
    
    print("\n" + analyzer.generate_report(result))
    print("\n✅ 测试完成!")