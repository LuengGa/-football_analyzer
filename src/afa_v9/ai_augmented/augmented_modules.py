"""
AFA v9.x AI原生化升级方案
==========================

目标: 将系统从 L2.9 提升到 L4.0+

升级模块:
1. Execution Engine - LLM动态决策
2. Bankroll Manager - LLM动态Kelly
3. 六层分析器 - LLM动态权重
4. Poisson模型 - LLM增强
5. 策略回测 - LLM自动生成
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1. LLM决策引擎 - 动态投注决策
# ============================================================================

@dataclass
class LLMDecisionContext:
    """LLM决策上下文"""
    match_info: Dict[str, Any]      # 比赛信息
    odds_data: Dict[str, Any]       # 赔率数据
    analysis_results: Dict[str, Any] # 分析结果
    bankroll_status: Dict[str, Any] # 资金状态
    market_sentiment: str = ""      # 市场情绪
    news_impact: str = ""           # 新闻影响
    historical_patterns: List[str] = None  # 历史模式

    def __post_init__(self):
        if self.historical_patterns is None:
            self.historical_patterns = []


class LLMBettingDecider:
    """
    LLM投注决策器

    替代传统规则引擎，让LLM综合分析所有因素做出决策
    """

    def __init__(self, llm_gateway=None):
        from src.core.llm.gateway import LLM_GATEWAY
        self.llm = llm_gateway or LLM_GATEWAY

    def decide(
        self,
        context: LLMDecisionContext,
        require_justification: bool = True
    ) -> Dict[str, Any]:
        """
        LLM决策

        返回:
        {
            "decision": "bet" | "skip" | "hedge",
            "confidence": 0.0-1.0,
            "stake_fraction": 0.0-1.0,
            "selection": "home" | "draw" | "away",
            "reasoning": "...",
            "risk_factors": [...],
            "market_factors": [...]
        }
        """

        prompt = self._build_decision_prompt(context)
        system = self._build_decision_system()

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="betting_decision"
            )

            return self._parse_decision(response)

        except Exception as e:
            logger.error(f"LLM决策失败: {e}")
            return {
                "decision": "skip",
                "confidence": 0.0,
                "reasoning": f"LLM不可用: {e}"
            }

    def _build_decision_prompt(self, ctx: LLMDecisionContext) -> str:
        """构建决策提示词"""

        match = ctx.match_info
        odds = ctx.odds_data
        analysis = ctx.analysis_results
        bankroll = ctx.bankroll_status

        return f"""
# 投注决策分析

## 比赛信息
主队: {match.get('home_team', 'N/A')}
客队: {match.get('away_team', 'N/A')}
联赛: {match.get('league', 'N/A')}
时间: {match.get('datetime', 'N/A')}

## 赔率数据
胜平负赔率:
  主胜: {odds.get('home_odds', 'N/A')}
  平局: {odds.get('draw_odds', 'N/A')}
  客胜: {odds.get('away_odds', 'N/A')}

亚洲盘口: {odds.get('asian_handicap', 'N/A')}
大小球: {odds.get('over_under', 'N/A')}

## 分析结果
六层分析: {analysis.get('six_layer', {})}
价值评估: {analysis.get('value_edge', 'N/A')}
Poisson预测: {analysis.get('poisson', {})}
历史战绩: {analysis.get('head_to_head', 'N/A')}

## 资金状态
余额: ¥{bankroll.get('balance', 0):,.2f}
今日投注: {bankroll.get('daily_bets', 0)}/{bankroll.get('max_daily', 10)}
ROI: {bankroll.get('roi', 0)*100:.1f}%

## 市场情绪
{ctx.market_sentiment or '暂无数据'}

## 新闻影响
{ctx.news_impact or '暂无数据'}

## 历史模式
{chr(10).join(f"- {p}" for p in ctx.historical_patterns[:5]) if ctx.historical_patterns else '无'}

---

请综合以上信息，做出投注决策:

1. 是否投注? (bet/skip/hedge)
2. 如果投注，投注哪个选项?
3. 投注金额比例 (0-100%)
4. 置信度 (0-100%)
5. 决策理由 (100字以上)
6. 风险因素
7. 市场因素

以JSON格式返回:
{{
  "decision": "bet|skip|hedge",
  "selection": "home|draw|away",
  "stake_fraction": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "...",
  "risk_factors": [...],
  "market_factors": [...]
}}
"""

    def _build_decision_system(self) -> str:
        return """你是一个专业的足球投注决策AI。

你的决策原则:
1. 价值优先 - 只在有正期望值时投注
2. 风险控制 - 不超过资金的5%单次投注
3. 多元化 - 分散投注降低风险
4. 理性决策 - 不受情绪和市场炒作影响

决策流程:
1. 分析赔率是否偏离合理区间
2. 结合分析结果评估概率
3. 计算价值优势 (预测概率 - 隐含概率)
4. 考虑资金管理限制
5. 综合所有因素做最终决策

记住:
- 低于3%的价值优势通常不值得投注
- 高赔率意味着低概率，需要更高置信度
- 连胜时要控制贪婪，连败时要防止冒进
"""

    def _parse_decision(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        import json
        import re

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "decision": data.get("decision", "skip"),
                    "selection": data.get("selection", ""),
                    "stake_fraction": float(data.get("stake_fraction", 0)),
                    "confidence": float(data.get("confidence", 0)),
                    "reasoning": data.get("reasoning", ""),
                    "risk_factors": data.get("risk_factors", []),
                    "market_factors": data.get("market_factors", []),
                    "llm_raw": response[:500]
                }
        except:
            pass

        return {
            "decision": "skip",
            "confidence": 0,
            "reasoning": response[:200],
            "llm_raw": response[:500]
        }


# ============================================================================
# 2. LLM动态Kelly - 自适应资金管理
# ============================================================================

class LLMDynamicKelly:
    """
    LLM动态Kelly计算器

    根据市场状态、比赛特征、历史表现动态调整Kelly参数
    """

    def __init__(self, llm_gateway=None):
        from src.core.llm.gateway import LLM_GATEWAY
        self.llm = llm_gateway or LLM_GATEWAY
        self.base_kelly_multiplier = 0.1  # 基础 Kelly 分数

    def calculate(
        self,
        odds: float,
        predicted_prob: float,
        confidence: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM增强的Kelly计算

        考虑因素:
        - 基础Kelly值
        - 预测置信度
        - 市场流动性
        - 历史表现调整
        - 资金状态
        """

        base_kelly = self._calculate_base_kelly(odds, predicted_prob)

        if context:
            prompt = self._build_kelly_adjustment_prompt(
                base_kelly, odds, predicted_prob, confidence, context
            )
            adjustment = self._get_llm_adjustment(prompt)
        else:
            adjustment = {"multiplier": 1.0, "reasoning": "无上下文，使用基础值"}

        adjusted_kelly = base_kelly * adjustment["multiplier"]
        recommended_stake = adjusted_kelly * (context.get("balance", 10000) if context else 10000)

        return {
            "base_kelly": base_kelly,
            "adjusted_kelly": adjusted_kelly,
            "multiplier": adjustment["multiplier"],
            "recommended_stake": recommended_stake,
            "reasoning": adjustment["reasoning"],
            "confidence_factor": confidence,
            "value_edge": predicted_prob - (1/odds)
        }

    def _calculate_base_kelly(self, odds: float, prob: float) -> float:
        """基础Kelly公式"""
        if odds <= 1 or prob <= 0:
            return 0
        b = odds - 1
        p = prob
        q = 1 - prob
        kelly = (b * p - q) / b
        return max(0, kelly)

    def _build_kelly_adjustment_prompt(
        self,
        base_kelly: float,
        odds: float,
        prob: float,
        confidence: float,
        context: Dict
    ) -> str:
        """构建Kelly调整提示词"""

        return f"""
# Kelly参数动态调整

## 当前投注
赔率: {odds}
预测概率: {prob*100:.1f}%
置信度: {confidence*100:.1f}%
基础Kelly: {base_kelly*100:.2f}%

## 上下文信息
资金余额: ¥{context.get('balance', 0):,.2f}
近期ROI: {context.get('recent_roi', 0)*100:.1f}%
连胜/连败: {context.get('streak', 'N/A')}
今日投注数: {context.get('daily_bets', 0)}

## 市场状态
市场热度: {context.get('market_heat', 'N/A')}
赔率变化: {context.get('odds_movement', 'N/A')}
庄家倾向: {context.get('bookmaker_bias', 'N/A')}

## 比赛特征
联赛类型: {context.get('league_type', 'N/A')}
比赛重要性: {context.get('match_importance', 'N/A')}
主客场因素: {context.get('home_advantage', 'N/A')}

---

请根据以上信息，决定Kelly调整系数:

1. 如果近期表现好，可适当提高 (1.0-1.5)
2. 如果连败，应降低风险 (0.5-0.8)
3. 如果市场过热，应保守 (0.5-0.7)
4. 如果置信度极高，可适当提高

返回JSON:
{{
  "multiplier": 0.5-1.5,
  "reasoning": "调整理由",
  "risk_level": "low|medium|high"
}}
"""

    def _get_llm_adjustment(self, prompt: str) -> Dict:
        """获取LLM调整建议"""
        system = "你是一个专业的资金管理AI，负责动态调整投注比例。原则是风险控制优先。"

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="kelly_adjustment"
            )

            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "multiplier": float(data.get("multiplier", 1.0)),
                    "reasoning": data.get("reasoning", ""),
                    "risk_level": data.get("risk_level", "medium")
                }
        except Exception as e:
            logger.warning(f"LLM调整失败: {e}")

        return {"multiplier": 1.0, "reasoning": "LLM不可用"}


# ============================================================================
# 3. LLM动态六层分析 - 自适应权重
# ============================================================================

class LLMDynamicSixLayer:
    """
    LLM动态六层分析器

    根据比赛上下文动态调整各层权重
    """

    DEFAULT_LAYERS = [
        "odds_structure",      # 赔率结构
        "market_movement",      # 市场动向
        "probability_model",    # 概率模型
        "historical_pattern",    # 历史模式
        "sentiment_analysis",   # 情绪分析
        "external_factors"      # 外部因素
    ]

    def __init__(self, llm_gateway=None):
        from src.core.llm.gateway import LLM_GATEWAY
        self.llm = llm_gateway or LLM_GATEWAY
        self.base_weights = {layer: 1.0 for layer in self.DEFAULT_LAYERS}

    def analyze(
        self,
        match_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM增强的六层分析

        1. LLM确定哪些层更重要
        2. LLM调整各层权重
        3. LLM综合各层结果
        """

        if context:
            adjusted_weights = self._get_adjusted_weights(match_data, context)
        else:
            adjusted_weights = self.base_weights.copy()

        layers_result: Dict[str, Any] = {}
        total_score: float = 0.0
        total_weight: float = 0.0

        for layer_name in self.DEFAULT_LAYERS:
            weight = adjusted_weights.get(layer_name, 1.0)
            layer_result = self._analyze_layer(layer_name, match_data)

            layers_result[layer_name] = {
                "score": layer_result["score"],
                "weight": weight,
                "weighted_score": layer_result["score"] * weight,
                "insights": layer_result.get("insights", []),
                "confidence": layer_result.get("confidence", 0.5)
            }

            total_score += layer_result["score"] * weight
            total_weight += weight

        final_score = total_score / total_weight if total_weight > 0 else 0

        return {
            "final_score": final_score,
            "layers": layers_result,
            "weights": adjusted_weights,
            "recommendation": self._generate_recommendation(final_score, layers_result)
        }

    def _get_adjusted_weights(
        self,
        match_data: Dict,
        context: Dict
    ) -> Dict[str, float]:
        """LLM动态调整权重"""

        prompt = f"""
# 六层分析权重调整

## 比赛信息
主队: {match_data.get('home_team', 'N/A')}
客队: {match_data.get('away_team', 'N/A')}
联赛: {match_data.get('league', 'N/A')}

## 上下文
比赛类型: {context.get('match_type', 'league')}
重要程度: {context.get('importance', 'normal')}
市场状态: {context.get('market_state', 'normal')}
球队状态: {context.get('team_form', 'normal')}

## 当前权重
赔率结构: 1.0
市场动向: 1.0
概率模型: 1.0
历史模式: 1.0
情绪分析: 1.0
外部因素: 1.0

---

请根据比赛特点调整各层权重:

原则:
- 杯赛决赛: 提高外部因素、历史模式权重
- 德比战: 提高情绪分析权重
- 弱队vs强队: 提高赔率结构、市场动向权重
- 连胜/连败: 提高/降低情绪分析权重

返回JSON:
{{
  "odds_structure": 0.5-1.5,
  "market_movement": 0.5-1.5,
  "probability_model": 0.5-1.5,
  "historical_pattern": 0.5-1.5,
  "sentiment_analysis": 0.5-1.5,
  "external_factors": 0.5-1.5,
  "reasoning": "调整理由"
}}
"""

        system = "你是一个专业的足球分析AI，负责根据比赛特点调整分析权重。"

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="weight_adjustment"
            )

            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {k: float(v) for k, v in data.items() if k != "reasoning"}
        except Exception as e:
            logger.warning(f"LLM权重调整失败: {e}")

        return self.base_weights.copy()  # type: ignore[return-value,no-any-return]

    def _analyze_layer(self, layer: str, data: Dict) -> Dict:
        """分析单个层"""
        return {
            "score": 0.5,
            "insights": [],
            "confidence": 0.5
        }

    def _generate_recommendation(self, score: float, layers: Dict) -> str:
        """生成推荐"""
        if score >= 0.7:
            return "强烈建议投注"
        elif score >= 0.6:
            return "可以考虑投注"
        elif score >= 0.4:
            return "谨慎观望"
        else:
            return "不建议投注"


# ============================================================================
# 4. LLM增强Poisson - 上下文感知预测
# ============================================================================

class LLMEnhancedPoisson:
    """
    LLM增强的Poisson模型

    LLM根据上下文调整参数，提供更准确的预测
    """

    def __init__(self, llm_gateway=None):
        from src.core.llm.gateway import LLM_GATEWAY
        self.llm = llm_gateway or LLM_GATEWAY

    def predict(
        self,
        home_team: str,
        away_team: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM增强的进球预测

        1. 获取基础Poisson预测
        2. LLM根据上下文调整
        3. 生成概率分布和预期进球
        """

        base_prediction = self._get_base_poisson(home_team, away_team)

        if context:
            adjusted = self._llm_adjust_prediction(
                base_prediction, home_team, away_team, context
            )
        else:
            adjusted = base_prediction.copy()

        return self._generate_prediction_report(base_prediction, adjusted, context)

    def _get_base_poisson(self, home: str, away: str) -> Dict:
        """获取基础Poisson预测"""
        from src.calculations.pro.poisson_model import EnhancedPoissonGoalModel as PoissonGoalModel

        model = PoissonGoalModel()

        home_stats = model.get_team_info(home)
        away_stats = model.get_team_info(away)

        if home_stats and away_stats:
            home_expected = (home_stats.attack + away_stats.defense) / 2
            away_expected = (away_stats.attack + home_stats.defense) / 2
        else:
            home_expected = 1.5
            away_expected = 1.2

        return {
            "home_expected_goals": home_expected,
            "away_expected_goals": away_expected,
            "home_probabilities": self._poisson_distribution(home_expected),
            "away_probabilities": self._poisson_distribution(away_expected),
            "correct_score_probs": self._calculate_correct_score(home_expected, away_expected)
        }

    def _poisson_distribution(self, lambda_val: float) -> Dict[int, float]:
        """计算Poisson分布"""
        from math import exp, factorial

        probs = {}
        for goals in range(8):
            probs[goals] = (exp(-lambda_val) * (lambda_val ** goals)) / factorial(goals)
        return probs

    def _calculate_correct_score(self, home_lambda: float, away_lambda: float) -> Dict:
        """计算比分概率"""
        home_probs = self._poisson_distribution(home_lambda)
        away_probs = self._poisson_distribution(away_lambda)

        scores = {}
        for hg in range(6):
            for ag in range(6):
                scores[f"{hg}-{ag}"] = home_probs.get(hg, 0) * away_probs.get(ag, 0)

        return dict(sorted(scores.items(), key=lambda x: -x[1])[:15])

    def _llm_adjust_prediction(
        self,
        base: Dict,
        home: str,
        away: str,
        context: Dict
    ) -> Dict:
        """LLM调整预测"""

        prompt = f"""
# Poisson预测调整

## 基础预测
主队({home})预期进球: {base['home_expected_goals']:.2f}
客队({away})预期进球: {base['away_expected_goals']:.2f}

## 上下文信息
主队近期状态: {context.get('home_form', 'N/A')}
客队近期状态: {context.get('away_form', 'N/A')}
主队伤停: {context.get('home_injuries', 'N/A')}
客队伤停: {context.get('away_injuries', 'N/A')}
天气: {context.get('weather', 'N/A')}
比赛重要性: {context.get('importance', 'N/A')}

---

请根据上下文调整预期进球数:

返回JSON:
{{
  "home_goals_adjusted": 0.5-3.0,
  "away_goals_adjusted": 0.5-3.0,
  "adjustment_reasoning": "...",
  "confidence_in_adjustment": 0.0-1.0
}}
"""

        system = "你是一个专业的足球分析AI，负责调整进球预测。考虑伤停、状态、天气等因素。"

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="poisson_adjustment"
            )

            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "home_goals_adjusted": float(data.get("home_goals_adjusted", base['home_expected_goals'])),
                    "away_goals_adjusted": float(data.get("away_goals_adjusted", base['away_expected_goals'])),
                    "reasoning": data.get("adjustment_reasoning", ""),
                    "confidence": float(data.get("confidence_in_adjustment", 0.5))
                }
        except Exception as e:
            logger.warning(f"LLM调整失败: {e}")

        return {
            "home_goals_adjusted": base['home_expected_goals'],
            "away_goals_adjusted": base['away_expected_goals'],
            "reasoning": "LLM不可用",
            "confidence": 0.5
        }

    def _generate_prediction_report(
        self,
        base: Dict,
        adjusted: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """生成预测报告"""
        return {
            "base_prediction": base,
            "adjusted_prediction": adjusted,
            "home_win_prob": adjusted.get("home_goals_adjusted", base['home_expected_goals']) /
                             (adjusted.get("home_goals_adjusted", base['home_expected_goals']) +
                              adjusted.get("away_goals_adjusted", base['away_expected_goals']) + 0.001),
            "context_applied": context is not None,
            "report": self._generate_natural_language_report(base, adjusted, context)
        }

    def _generate_natural_language_report(
        self,
        base: Dict,
        adjusted: Dict,
        context: Optional[Dict]
    ) -> str:
        """生成自然语言报告"""
        home_adjusted = adjusted.get("home_goals_adjusted", base['home_expected_goals'])
        away_adjusted = adjusted.get("away_goals_adjusted", base['away_expected_goals'])

        report = f"""
## 进球预测报告

### 基础Poisson模型
主队预期进球: {base['home_expected_goals']:.2f}
客队预期进球: {base['away_expected_goals']:.2f}

### LLM调整后
主队预期进球: {home_adjusted:.2f}
客队预期进球: {away_adjusted:.2f}

调整理由: {adjusted.get('reasoning', '无')}
调整置信度: {adjusted.get('confidence', 0.5)*100:.0f}%

### 概率预测
"""
        return report


# ============================================================================
# 5. LLM策略生成器 - 自动发现和优化策略
# ============================================================================

class LLMStrategyGenerator:
    """
    LLM策略生成器

    根据历史数据和回测结果自动生成和优化策略
    """

    def __init__(self, llm_gateway=None):
        from src.core.llm.gateway import LLM_GATEWAY
        self.llm = llm_gateway or LLM_GATEWAY

    def generate_strategy(
        self,
        historical_data: List[Dict],
        target_league: str = "EPL",
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM生成投注策略

        1. 分析历史数据模式
        2. 发现潜在价值机会
        3. 生成具体策略规则
        4. 提供回测参数
        """

        patterns = self._discover_patterns(historical_data)
        opportunities = self._identify_opportunities(patterns)
        strategy = self._generate_strategy_rules(opportunities, constraints)

        return {
            "patterns_discovered": patterns,
            "opportunities": opportunities,
            "strategy": strategy,
            "backtest_params": self._generate_backtest_params(strategy, target_league)
        }

    def _discover_patterns(self, data: List[Dict]) -> List[Dict]:
        """LLM发现数据模式"""

        prompt = f"""
# 历史数据模式发现

分析以下足球比赛数据，发现有价值的投注模式:

数据样本 (前20场):
{self._format_sample_data(data[:20])}

请发现以下模式:
1. 特定联赛的投注模式
2. 主客场表现差异
3. 赔率区间与结果的关系
4. 特定球队的表现规律
5. 时间/季节性模式

返回JSON数组格式:
[
  {{
    "pattern": "模式描述",
    "confidence": 0.0-1.0,
    "evidence": "支持证据",
    "betting_implication": "投注含义"
  }}
]
"""

        system = "你是一个专业的足球数据分析师，负责从历史数据中发现投注价值模式。"

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="pattern_discovery"
            )

            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"模式发现失败: {e}")

        return []  # type: ignore[return-value]

    def _identify_opportunities(self, patterns: List[Dict]) -> List[Dict]:
        """识别潜在机会"""
        opportunities: List[Dict[str, Any]] = []

        for p in patterns:
            if p.get("confidence", 0) > 0.6:
                opportunities.append({
                    "pattern": p.get("pattern"),
                    "expected_edge": 0.03,
                    "min_odds": 1.8,
                    "max_odds": 4.0,
                    "bet_type": "value_bet"
                })

        return opportunities

    def _generate_strategy_rules(
        self,
        opportunities: List[Dict],
        constraints: Optional[Dict]
    ) -> Dict:
        """生成策略规则"""

        if not opportunities:
            return {
                "name": "保守策略",
                "rules": ["只投注高置信度机会"],
                "risk_level": "low"
            }

        prompt = f"""
# 投注策略生成

基于发现的机会生成具体策略:

机会列表:
{chr(10).join(f"- {o['pattern']}" for o in opportunities)}

约束条件:
- 最大单次投注比例: {constraints.get('max_stake_pct', 5) if constraints else 5}%
- 最低价值阈值: {constraints.get('min_value', 3) if constraints else 3}%
- 目标ROI: {constraints.get('target_roi', 5) if constraints else 5}%

请生成策略:
1. 策略名称
2. 具体规则 (3-5条)
3. 入场条件
4. 止损条件
5. 风险管理

返回JSON:
{{
  "name": "策略名称",
  "rules": ["规则1", "规则2", ...],
  "entry_conditions": [...],
  "stop_loss": "止损条件",
  "risk_level": "low|medium|high",
  "expected_roi": "预期ROI",
  "confidence": 0.0-1.0
}}
"""

        system = "你是一个专业的投注策略设计师，负责根据数据分析结果生成可执行的投注策略。"

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=system,
                task_type="strategy_generation"
            )

            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"策略生成失败: {e}")

        return {
            "name": "默认策略",
            "rules": ["等待LLM策略生成"],
            "risk_level": "medium"
        }

    def _generate_backtest_params(
        self,
        strategy: Dict,
        league: str
    ) -> Dict:
        """生成回测参数"""
        return {
            "league": league,
            "strategy_name": strategy.get("name", "unknown"),
            "rules": strategy.get("rules", []),
            "period": "2024",
            "initial_capital": 10000,
            "kelly_fraction": 0.1
        }

    def _format_sample_data(self, data: List[Dict]) -> str:
        """格式化样本数据"""
        lines = []
        for d in data:
            line = f"{d.get('home_team', '?')} {d.get('home_goals', '?')}-{d.get('away_goals', '?')} {d.get('away_team', '?')}"
            lines.append(line)
        return '\n'.join(lines)


# ============================================================================
# 6. 统一的AI增强执行引擎
# ============================================================================

class AIAugmentedExecutionEngine:
    """
    AI增强执行引擎

    整合以上所有AI能力，提供端到端的投注决策
    """

    def __init__(self):
        self.decider = LLMBettingDecider()
        self.dynamic_kelly = LLMDynamicKelly()
        self.six_layer = LLMDynamicSixLayer()
        self.poisson = LLMEnhancedPoisson()
        self.strategy_gen = LLMStrategyGenerator()

    def make_decision(
        self,
        match_data: Dict[str, Any],
        odds_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        完整的AI决策流程

        1. 六层分析 (动态权重)
        2. Poisson预测 (LLM增强)
        3. LLM综合决策
        4. 动态Kelly计算
        """

        six_layer_result = self.six_layer.analyze(match_data, context)
        poisson_result = self.poisson.predict(
            match_data.get("home_team"),
            match_data.get("away_team"),
            context
        )

        bankroll_context = context.get("bankroll") if context else None
        bankroll_dict: Dict[str, Any] = bankroll_context if isinstance(bankroll_context, dict) else {}

        llm_context = LLMDecisionContext(
            match_info=match_data,
            odds_data=odds_data,
            analysis_results={
                "six_layer": six_layer_result,
                "poisson": poisson_result,
                "value_edge": self._calculate_value_edge(
                    six_layer_result.get("final_score", 0.5),
                    odds_data
                )
            },
            bankroll_status=bankroll_dict,
            market_sentiment=context.get("market_sentiment", "") if context else "",
            news_impact=context.get("news_impact", "") if context else "",
            historical_patterns=context.get("patterns", []) if context else []
        )

        decision = self.decider.decide(llm_context)

        if decision.get("decision") == "bet":
            kelly_result = self.dynamic_kelly.calculate(
                odds=odds_data.get(decision.get("selection", "home_odds"), 2.0),
                predicted_prob=six_layer_result.get("final_score", 0.5),
                confidence=decision.get("confidence", 0.5),
                context={
                    "balance": context.get("bankroll", {}).get("balance", 10000) if context else 10000,
                    "recent_roi": context.get("bankroll", {}).get("roi", 0) if context else 0,
                }
            )
        else:
            kelly_result = {"recommended_stake": 0}

        return {
            "decision": decision,
            "six_layer_analysis": six_layer_result,
            "poisson_prediction": poisson_result,
            "kelly_calculation": kelly_result,
            "final_stake": kelly_result.get("recommended_stake", 0),
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_value_edge(self, predicted_prob: float, odds: Dict) -> float:
        """计算价值优势"""
        home_odds = odds.get("home_odds", 2.0)
        implied_prob = 1 / home_odds if home_odds > 1 else 0.5
        return predicted_prob - implied_prob


# ============================================================================
# 导出
# ============================================================================

LLM_DECIDER = LLMBettingDecider()
LLM_DYNAMIC_KELLY = LLMDynamicKelly()
LLM_SIX_LAYER = LLMDynamicSixLayer()
LLM_POISSON = LLMEnhancedPoisson()
LLM_STRATEGY_GEN = LLMStrategyGenerator()
AUGMENTED_ENGINE = AIAugmentedExecutionEngine()

__all__ = [
    "LLMBettingDecider",
    "LLMDynamicKelly",
    "LLMDynamicSixLayer",
    "LLMEnhancedPoisson",
    "LLMStrategyGenerator",
    "AIAugmentedExecutionEngine",
    "LLM_DECIDER",
    "LLM_DYNAMIC_KELLY",
    "LLM_SIX_LAYER",
    "LLM_POISSON",
    "LLM_STRATEGY_GEN",
    "AUGMENTED_ENGINE",
]
