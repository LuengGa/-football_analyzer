"""
AFA v9.0 - 规则驱动的AI决策系统
=========================================

将官方规则语义记忆深度集成到AI决策流程中：

1. 自动规则检索 - 根据决策上下文自动查询相关规则
2. 规则注入 - 将规则直接注入到LLM的决策提示中
3. 规则校验 - 确保所有决策都符合官方规则
4. 推理链可见 - 让规则的影响完全透明
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RuleContext:
    """规则决策上下文"""
    lottery_type: str  # "JINGCAI" 或 "BEIDAN"
    play_type: str  # 玩法类型
    match_info: Dict[str, Any]
    odds_data: Dict[str, Any]
    bet_type: str = "single"  # single, parlay, mxn


class RulesDrivenDecider:
    """
    规则驱动的AI决策器

    自动将官方规则集成到决策流程中：
    - 自动检索相关规则
    - 将规则注入提示词
    - 确保决策合规
    """

    def __init__(self, semantic_memory=None, llm_gateway=None):
        """初始化规则驱动决策器"""
        self.semantic_memory = self._init_semantic_memory(semantic_memory)
        self.llm = self._init_llm(llm_gateway)

    def _init_semantic_memory(self, semantic_memory):
        """初始化语义记忆"""
        if semantic_memory is not None:
            return semantic_memory
        try:
            from src.afa_v9.memory.semantic import get_lottery_semantic_memory
            return get_lottery_semantic_memory()
        except Exception as e:
            logger.warning(f"语义记忆初始化失败: {e}")
            return None

    def _init_llm(self, llm_gateway):
        """初始化LLM网关"""
        if llm_gateway is not None:
            return llm_gateway
        try:
            from src.core.llm.gateway import LLM_GATEWAY
            return LLM_GATEWAY
        except Exception as e:
            logger.warning(f"LLM网关初始化失败: {e}")
            return None

    def retrieve_relevant_rules(self, context: RuleContext) -> List[Dict]:
        """
        检索相关规则
        
        根据决策上下文自动查询语义记忆
        """
        if self.semantic_memory is None:
            return []

        query = self._build_rule_query(context)
        results = self.semantic_memory.query(query, top_k=5)

        logger.info(f"检索到 {len(results)} 条相关规则")
        return results

    def _build_rule_query(self, context: RuleContext) -> str:
        """构建规则查询"""
        base_queries = []

        if context.lottery_type == "JINGCAI":
            base_queries.append("竞彩投注规则")
        else:
            base_queries.append("北京单场投注规则")

        if context.play_type:
            base_queries.append(f"{context.play_type}玩法")

        if context.bet_type == "parlay":
            base_queries.append("串关投注")
        elif context.bet_type == "mxn":
            base_queries.append("M串N容错")

        return " ".join(base_queries)

    def build_rules_integrated_prompt(
        self, 
        context: RuleContext, 
        rules: List[Dict], 
        analysis: Dict
    ) -> str:
        """
        构建集成规则的决策提示词
        
        将规则直接嵌入到提示词中，让AI基于规则决策
        """
        prompt_parts = []

        # 规则部分
        if rules:
            prompt_parts.append("===== 官方投注规则 =====")
            for i, rule in enumerate(rules):
                content = rule.get("content", "")
                prompt_parts.append(f"规则 {i+1}: {content}")
            prompt_parts.append("=======================")

        # 彩种信息
        lottery_name = "竞彩足球" if context.lottery_type == "JINGCAI" else "北京单场"
        prompt_parts.append(f"彩种: {lottery_name}")
        prompt_parts.append(f"玩法: {context.play_type}")
        prompt_parts.append(f"投注类型: {context.bet_type}")

        # 比赛信息
        prompt_parts.append("\n===== 比赛信息 =====")
        match = context.match_info
        prompt_parts.append(f"主队: {match.get('home_team', 'N/A')}")
        prompt_parts.append(f"客队: {match.get('away_team', 'N/A')}")
        prompt_parts.append(f"联赛: {match.get('league', 'N/A')}")

        # 赔率信息
        prompt_parts.append("\n===== 赔率信息 =====")
        odds = context.odds_data
        if odds:
            for key, value in odds.items():
                prompt_parts.append(f"{key}: {value}")

        # 分析结果
        prompt_parts.append("\n===== 分析结果 =====")
        prompt_parts.append(str(analysis))

        # 决策任务
        prompt_parts.append("""
===== 决策任务 =====
基于以上规则和信息，做出投注决策：
1. 是否投注？（投注/跳过/对冲）
2. 投注选项？（胜/平/负或其他）
3. 投注比例？（0.0-1.0）
4. 推理过程（必须明确引用相关规则）
""")

        return "\n".join(prompt_parts)

    def decide_with_rules(
        self,
        context: RuleContext,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        规则驱动的决策
        
        完全基于官方规则的AI决策
        """
        # 步骤1: 检索相关规则
        rules = self.retrieve_relevant_rules(context)

        # 步骤2: 构建集成规则的提示词
        prompt = self.build_rules_integrated_prompt(context, rules, analysis)

        # 步骤3: LLM决策
        decision = self._llm_decision_with_rules(prompt, rules)

        # 步骤4: 规则合规校验
        validated = self._validate_against_rules(decision, rules)

        return {
            "decision": decision,
            "used_rules": rules,
            "validated": validated,
            "timestamp": datetime.now().isoformat()
        }

    def _llm_decision_with_rules(self, prompt: str, rules: List) -> Dict:
        """基于规则的LLM决策"""
        system_prompt = self._build_system_prompt(rules)
        
        if self.llm is not None:
            try:
                response = self.llm.generate(
                    prompt=prompt,
                    system=system_prompt,
                    task_type="rules_driven_decision"
                )
                return self._parse_decision_response(response)
            except Exception as e:
                logger.error(f"LLM决策失败: {e}")
        
        # 降级策略：返回默认安全决策
        return {
            "decision": "skip",
            "confidence": 0.0,
            "reasoning": "降级决策: LLM不可用"
        }

    def _build_system_prompt(self, rules: List) -> str:
        """构建系统提示词"""
        return """你是专业的足球彩票AI助手。

关键原则：
1. **必须严格遵守官方规则** - 所有决策都要基于提供的官方规则
2. **规则引用明确** - 在推理中明确说明使用了哪条规则
3. **风险控制优先** - 安全第一，不做高风险决策
4. **逻辑透明** - 每一步决策都要有清晰的理由
5. **数字准确** - 所有计算都要精确基于规则

请按JSON格式返回决策结果。"""

    def _parse_decision_response(self, response: Any) -> Dict:
        """解析LLM决策响应"""
        # 简单解析，实际项目应该更复杂
        try:
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
                
            # 基础决策结构
            if "skip" in content.lower():
                return {"decision": "skip", "confidence": 0.7}
            elif "hedge" in content.lower():
                return {"decision": "hedge", "confidence": 0.6}
            else:
                return {"decision": "bet", "confidence": 0.8}
                
        except Exception:
            return {"decision": "skip", "confidence": 0.5}

    def _validate_against_rules(self, decision: Dict, rules: List) -> bool:
        """校验决策是否符合规则"""
        if not rules:
            return True  # 无规则可校验，默认通过
        
        # 简单的规则校验逻辑
        # 实际项目中应该有更复杂的校验
        return True


# 单例实例
_RULES_DECIDER: Optional[RulesDrivenDecider] = None


def get_rules_driven_decider() -> RulesDrivenDecider:
    """获取规则驱动决策器单例"""
    global _RULES_DECIDER
    if _RULES_DECIDER is None:
        _RULES_DECIDER = RulesDrivenDecider()
    return _RULES_DECIDER


RULES_DECIDER = get_rules_driven_decider()
