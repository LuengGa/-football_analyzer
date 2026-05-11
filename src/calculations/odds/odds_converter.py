"""
OddsConverter - 赔率转换器（修正版）
基于官方权威资料实现赔率转换
"""
from typing import Dict, Any, List, Optional
import numpy as np


class OddsConverter:
    """赔率转换器 - 基于权威资料的正确实现"""
    
    # 欧赔区间 → 亚盘盘口 对应表（权威资料）
    ODDS_TO_HANDICAP_MAP = [
        {"min_odds": 1.15, "max_odds": 1.25, "handicap": 1.5, "win_rate": "66%+"},
        {"min_odds": 1.25, "max_odds": 1.35, "handicap": 1.5, "win_rate": "66%+"},
        {"min_odds": 1.35, "max_odds": 1.45, "handicap": 1.25, "win_rate": "61%-66%"},
        {"min_odds": 1.45, "max_odds": 1.60, "handicap": 1.0, "win_rate": "56%-62%"},
        {"min_odds": 1.60, "max_odds": 1.70, "handicap": 0.75, "win_rate": "53%-56%"},
        {"min_odds": 1.70, "max_odds": 1.90, "handicap": 0.5, "win_rate": "46%-53%"},
        {"min_odds": 1.90, "max_odds": 2.30, "handicap": 0.25, "win_rate": "39%-47%"},
        {"min_odds": 2.30, "max_odds": 2.60, "handicap": 0.0, "win_rate": "35%-39%"},
    ]
    
    def __init__(self):
        pass
    
    def european_to_probability(self, odds: float) -> float:
        """欧赔转概率"""
        if odds <= 1.0:
            return 0.0
        return 1.0 / odds
    
    def probability_to_european(self, prob: float) -> float:
        """概率转欧赔"""
        if prob <= 0:
            return 0.0
        return 1.0 / prob
    
    def get_asian_handicap_from_odds(self, odds: float) -> Dict[str, Any]:
        """
        根据欧赔获取对应的亚盘盘口（核心功能）
        
        根据权威资料：
        - 欧赔 1.15-1.25 → 球半(1.5)
        - 欧赔 1.25-1.35 → 球半(1.5)
        - 欧赔 1.35-1.45 → 一球/球半(1/1.5)
        - 欧赔 1.45-1.60 → 一球(1)
        - 欧赔 1.60-1.70 → 半球/一球(0.5/1)
        - 欧赔 1.70-1.90 → 半球(0.5)
        - 欧赔 1.90-2.30 → 平手/半球(0/0.5)
        - 欧赔 2.30-2.60 → 平手(0)
        """
        if odds < 1.15:
            return {"handicap": 2.0, "description": "两球", "win_rate": "70%+"}
        
        for mapping in self.ODDS_TO_HANDICAP_MAP:
            if mapping["min_odds"] <= odds < mapping["max_odds"]:
                return {
                    "handicap": mapping["handicap"],
                    "description": self._handicap_to_text(mapping["handicap"]),
                    "win_rate": mapping["win_rate"]
                }
        
        if odds >= 2.60:
            return {"handicap": -0.25, "description": "受让平/半", "win_rate": "<35%"}
        
        return {"handicap": 0.0, "description": "平手", "win_rate": "35%-39%"}
    
    def _handicap_to_text(self, handicap: float) -> str:
        """盘口转文字描述"""
        handicap_map = {
            0.0: "平手",
            0.25: "平/半",
            0.5: "半球",
            0.75: "半/一",
            1.0: "一球",
            1.25: "一/球半",
            1.5: "球半",
            1.75: "球半/两球",
            2.0: "两球"
        }
        return handicap_map.get(handicap, f"{handicap}")
    
    def european_to_asian_odds_simple(self, eu_odds: float, handicap: float) -> float:
        """
        简化的欧赔转亚盘赔率
        
        公式: 亚盘赔率 = 1 / 欧赔
        
        但需要注意：
        - 亚盘是"抽水"后的赔率，总返还率约90%
        - 需要根据盘口调整
        """
        if eu_odds <= 1.0:
            return 0.0
        
        # 基础转换
        asian_odds = 1.0 / eu_odds
        
        # 考虑盘口调整（简化版）
        if handicap > 0:
            # 让球方，赔率应该更高（因为赢的概率更大）
            adjustment = 1 + handicap * 0.05
            asian_odds = asian_odds * adjustment
        elif handicap < 0:
            # 受让方，赔率应该更低
            adjustment = 1 + handicap * 0.03
            asian_odds = asian_odds * adjustment
        
        return round(asian_odds, 3)
    
    def calculate_asian_water(self, eu_home: float, eu_away: float, handicap: float) -> Dict[str, float]:
        """
        计算亚盘水位
        
        权威公式:
        返还率 = 胜赔×平赔×负赔 / (胜赔×平赔 + 平赔×负赔 + 胜赔×负赔)
        
        水位 = 返还率 / 隐含概率
        """
        # 计算隐含概率
        prob_home = self.european_to_probability(eu_home)
        prob_away = self.european_to_probability(eu_away)
        
        # 归一化
        total = prob_home + prob_away
        prob_home_norm = prob_home / total
        prob_away_norm = prob_away / total
        
        # 亚盘返还率约90%
        return_rate = 0.90
        
        # 计算水位
        home_water = return_rate / prob_home_norm
        away_water = return_rate / prob_away_norm
        
        return {
            "上盘水位": round(home_water, 3),
            "下盘水位": round(away_water, 3),
            "返还率": f"{return_rate*100}%"
        }
    
    def jingcai_to_european(self, jingcai_odds: float) -> float:
        """
        竞彩赔率转欧赔
        
        竞彩返奖率约69%
        公式: 欧赔 = 竞彩赔率 / 0.69
        """
        if jingcai_odds <= 0:
            return 0.0
        return round(jingcai_odds / 0.69, 3)
    
    def european_to_jingcai(self, eu_odds: float) -> float:
        """
        欧赔转竞彩赔率
        
        公式: 竞彩赔率 = 欧赔 × 0.69
        """
        if eu_odds <= 0:
            return 0.0
        return round(eu_odds * 0.69, 3)
    
    def beidan_to_european(self, sp_value: float) -> float:
        """
        北单SP值转欧赔
        
        北单返奖率约65%
        公式: 欧赔 = SP值 / 0.65
        """
        if sp_value <= 0:
            return 0.0
        return round(sp_value / 0.65, 3)
    
    def european_to_beidan(self, eu_odds: float) -> float:
        """
        欧赔转北单SP值
        
        公式: SP值 = 欧赔 × 0.65
        """
        if eu_odds <= 0:
            return 0.0
        return round(eu_odds * 0.65, 3)


class ValueAnalyzer:
    """价值分析器"""
    
    def __init__(self):
        self.converter = OddsConverter()
    
    def analyze_value(
        self,
        eu_odds: Optional[float] = None,
        jingcai_odds: Optional[float] = None,
        beidan_sp: Optional[float] = None,
        handicap: float = 0.0
    ) -> Dict[str, Any]:
        """价值分析"""
        results = {
            "has_value": False,
            "opportunities": [],
            "conversions": {}
        }
        
        # 转换为欧赔比较
        normalized = {}
        
        if eu_odds:
            normalized["欧赔"] = eu_odds
            
            # 获取对应的理论盘口
            theoretical_handicap = self.converter.get_asian_handicap_from_odds(eu_odds)
            results["conversions"]["理论盘口"] = theoretical_handicap["description"]
        
        if jingcai_odds:
            eu_from_jc = self.converter.jingcai_to_european(jingcai_odds)
            normalized["竞彩转欧赔"] = eu_from_jc
            results["conversions"]["竞彩→欧赔"] = eu_from_jc
            
            if eu_odds:
                diff = eu_from_jc - eu_odds
                pct = (diff / eu_odds) * 100
                results["conversions"]["差异"] = f"{pct:+.2f}%"
                
                if abs(pct) > 5:
                    results["opportunities"].append({
                        "type": "竞彩vs欧赔",
                        "diff": f"{pct:+.2f}%",
                        "potential": "高" if abs(pct) > 10 else "中"
                    })
        
        if beidan_sp:
            eu_from_bd = self.converter.beidan_to_european(beidan_sp)
            normalized["北单转欧赔"] = eu_from_bd
            results["conversions"]["北单→欧赔"] = eu_from_bd
            
            if eu_odds:
                diff = eu_from_bd - eu_odds
                pct = (diff / eu_odds) * 100
                results["conversions"]["北单差异"] = f"{pct:+.2f}%"
                
                if abs(pct) > 5:
                    results["opportunities"].append({
                        "type": "北单vs欧赔",
                        "diff": f"{pct:+.2f}%",
                        "potential": "高" if abs(pct) > 10 else "中"
                    })
        
        if results["opportunities"]:
            results["has_value"] = True
        
        results["normalized"] = normalized
        return results


# 全局实例
_odds_converter = None
_value_analyzer = None

def get_odds_converter() -> OddsConverter:
    global _odds_converter
    if _odds_converter is None:
        _odds_converter = OddsConverter()
    return _odds_converter

def get_value_analyzer() -> ValueAnalyzer:
    global _value_analyzer
    if _value_analyzer is None:
        _value_analyzer = ValueAnalyzer()
    return _value_analyzer


if __name__ == "__main__":
    print("=" * 70)
    print("🔍 赔率转换器（修正版）测试")
    print("=" * 70)
    
    converter = get_odds_converter()
    analyzer = get_value_analyzer()
    
    # 测试1: 欧赔查盘口
    print("\n📊 测试1: 欧赔 → 亚盘盘口")
    print("-" * 50)
    
    test_odds = [1.20, 1.40, 1.55, 1.75, 2.00, 2.50]
    for odds in test_odds:
        result = converter.get_asian_handicap_from_odds(odds)
        print(f"欧赔 {odds} → {result['description']} (胜率{result['win_rate']})")
    
    # 测试2: 竞彩/北单转欧赔
    print("\n📊 测试2: 竞彩/北单 → 欧赔")
    print("-" * 50)
    
    jingcai = 1.55
    beidan = 2.50
    
    eu_from_jc = converter.jingcai_to_european(jingcai)
    eu_from_bd = converter.beidan_to_european(beidan)
    
    print(f"竞彩赔率 {jingcai} → 欧赔 {eu_from_jc}")
    print(f"北单SP {beidan} → 欧赔 {eu_from_bd}")
    
    # 测试3: 价值分析
    print("\n📊 测试3: 价值分析")
    print("-" * 50)
    
    result = analyzer.analyze_value(
        eu_odds=1.85,
        jingcai_odds=1.30,
        beidan_sp=1.20
    )
    
    print(f"分析结果:")
    print(f"  有价值机会: {result['has_value']}")
    print(f"  转换结果:")
    for k, v in result["conversions"].items():
        print(f"    {k}: {v}")
    if result["opportunities"]:
        print(f"  价值机会:")
        for opp in result["opportunities"]:
            print(f"    {opp['type']}: {opp['diff']} (潜在: {opp['potential']})")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成!")
    print("=" * 70)
