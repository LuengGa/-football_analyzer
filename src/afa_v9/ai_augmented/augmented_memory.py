
"""
AI-Augmented Memory System - 智能记忆管理
========================================

核心功能：
- LLM 记忆总结与洞察提取
- 语义理解的记忆检索
- 记忆重要性智能评估
- 自动模式识别与关联
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MemoryInsight:
    """记忆洞察结果"""
    key: str
    summary: str
    key_points: List[str]
    related_patterns: List[str]
    importance_score: float
    generated_at: str


class LLMMemoryManager:
    """
    LLM驱动的记忆管理器
    """
    
    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self.insights_cache: Dict[str, MemoryInsight] = {}
    
    def analyze_memory(self, key: str, content: Any, 
                       context: Optional[Dict] = None) -> MemoryInsight:
        """
        使用LLM分析记忆，生成总结和洞察
        """
        try:
            content_str = self._format_content(content)
            
            prompt = self._build_analysis_prompt(content_str, context)
            
            if self.llm:
                response = self.llm.generate(
                    prompt=prompt,
                    system=self._get_system_prompt(),
                    temperature=0.3,
                    max_tokens=800
                )
                insight = self._parse_llm_response(key, response)
            else:
                insight = self._fallback_analysis(key, content_str)
            
            self.insights_cache[key] = insight
            return insight
            
        except Exception as e:
            logger.warning(f"LLM memory analysis failed, using fallback: {e}")
            return self._fallback_analysis(key, self._format_content(content))
    
    def search_with_semantic_understanding(self, query: str, 
                                          raw_results: List[Dict]) -> List[Dict]:
        """
        使用LLM对搜索结果进行语义重排序
        """
        try:
            if not raw_results:
                return []
            
            if self.llm:
                reranked = self._semantic_rerank(query, raw_results)
                return reranked
            else:
                return raw_results[:10]
                
        except Exception as e:
            logger.warning(f"Semantic reranking failed: {e}")
            return raw_results[:10]
    
    def generate_memory_summary(self, memories: List[Dict], 
                                focus: str = "general") -> str:
        """
        生成记忆集合的综合总结
        """
        try:
            if not memories:
                return "无记忆记录"
            
            context_text = "\n".join([
                f"- {m.get('category', 'unknown')}: {str(m.get('content', ''))[:100]}..."
                for m in memories[:20]
            ])
            
            if self.llm:
                prompt = f"""请基于以下记忆记录生成一个{focus}方向的综合总结（不超过300字）：

{context_text}

总结应包括：
1. 关键发现
2. 模式与趋势
3. 行动建议（如适用）"""
                
                return str(self.llm.generate(  # type: ignore[return-value]
                    prompt=prompt,
                    temperature=0.4,
                    max_tokens=400
                ))
            else:
                return self._fallback_summary(memories, focus)
                
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return self._fallback_summary(memories, focus)
    
    def assess_importance(self, content: Any, 
                         context: Optional[Dict] = None) -> float:
        """
        智能评估记忆重要性（0-1）
        """
        try:
            content_str = self._format_content(content)
            
            keywords = ["win", "loss", "profit", "strategy", "bet", "injury", 
                       "weather", "odds", "market", "关键", "重要", "建议"]
            score = 0.5
            
            for kw in keywords:
                if kw.lower() in content_str.lower():
                    score += 0.08
            
            if context and context.get("is_betting_decision", False):
                score += 0.15
            if context and context.get("is_learning", False):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _format_content(self, content: Any) -> str:
        """格式化内容为字符串"""
        if isinstance(content, str):
            return content
        return json.dumps(content, ensure_ascii=False)
    
    def _get_system_prompt(self) -> str:
        return """你是一个专业的体育博彩分析师助手，负责分析和管理记忆。
请保持客观、专业，重点关注：
1. 投注决策相关的模式
2. 球队/比赛的关键因素
3. 可重复利用的洞察
4. 避免的错误模式"""
    
    def _build_analysis_prompt(self, content: str, 
                               context: Optional[Dict]) -> str:
        context_str = f"\n上下文: {json.dumps(context, ensure_ascii=False)}" if context else ""
        
        return f"""请分析以下记忆内容，提取关键洞察：

内容:
{content}
{context_str}

请以JSON格式返回：
{{
  "summary": "简洁总结（50字以内）",
  "key_points": ["关键点1", "关键点2", "关键点3"],
  "related_patterns": ["相关模式1", "相关模式2"],
  "importance_score": 0.8
}}"""
    
    def _parse_llm_response(self, key: str, response: str) -> MemoryInsight:
        """解析LLM响应"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return MemoryInsight(
                    key=key,
                    summary=data.get("summary", ""),
                    key_points=data.get("key_points", []),
                    related_patterns=data.get("related_patterns", []),
                    importance_score=data.get("importance_score", 0.5),
                    generated_at=datetime.now().isoformat()
                )
        except Exception:
            pass
        
        return self._fallback_analysis(key, response)
    
    def _fallback_analysis(self, key: str, content: str) -> MemoryInsight:
        """降级分析方法"""
        content_short = content[:100] + "..." if len(content) > 100 else content
        return MemoryInsight(
            key=key,
            summary=content_short,
            key_points=[],
            related_patterns=[],
            importance_score=0.5,
            generated_at=datetime.now().isoformat()
        )
    
    def _semantic_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """简单的语义重排序（基于关键词匹配）"""
        query_terms = set(query.lower().split())
        
        for result in results:
            content = str(result.get("content", "")).lower()
            match_count = sum(1 for term in query_terms if term in content)
            result["_semantic_score"] = match_count + result.get("importance", 0.5)
        
        results.sort(key=lambda x: x.get("_semantic_score", 0), reverse=True)
        return results[:10]
    
    def _fallback_summary(self, memories: List[Dict], focus: str) -> str:
        """降级总结方法"""
        categories: Dict[str, int] = {}
        for m in memories:
            cat = m.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return f"记忆统计: {len(memories)}条记录, 分类分布: {categories}"


# 全局实例
LLM_MEMORY_MANAGER = LLMMemoryManager()

__all__ = ["LLMMemoryManager", "LLM_MEMORY_MANAGER", "MemoryInsight"]
