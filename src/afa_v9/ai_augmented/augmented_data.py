
"""
AI-Augmented Data System - 智能数据管理
======================================

核心功能：
- LLM 数据源质量评估与选择
- 智能数据优先级排序
- 自动数据源故障转移
- 数据质量监控与建议
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DataSourceQuality:
    """数据源质量评估"""
    source_name: str
    quality_score: float
    reliability: float
    freshness: float
    accuracy: float
    recommendations: List[str]
    last_evaluated: str


class LLMDataManager:
    """
    LLM驱动的数据管理器
    """
    
    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self.source_quality: Dict[str, DataSourceQuality] = {}
        self.source_stats: Dict[str, Dict] = {}
    
    def evaluate_data_source(self, source_name: str, 
                           data: Any, 
                           context: Optional[Dict] = None) -> DataSourceQuality:
        """
        评估数据源质量
        """
        try:
            data_str = self._format_data(data)
            
            if self.llm:
                prompt = self._build_evaluation_prompt(source_name, data_str, context)
                response = self.llm.generate(
                    prompt=prompt,
                    system=self._get_system_prompt(),
                    temperature=0.2,
                    max_tokens=600
                )
                quality = self._parse_quality_response(source_name, response)
            else:
                quality = self._fallback_evaluation(source_name, data)
            
            self.source_quality[source_name] = quality
            return quality
            
        except Exception as e:
            logger.warning(f"Source evaluation failed: {e}")
            return self._fallback_evaluation(source_name, data)
    
    def select_best_source(self, source_names: List[str], 
                          data_samples: Dict[str, Any],
                          priority: str = "accuracy") -> str:
        """
        选择最佳数据源
        """
        scores = {}
        
        for name in source_names:
            if name in self.source_quality:
                q = self.source_quality[name]
                if priority == "accuracy":
                    scores[name] = q.accuracy
                elif priority == "freshness":
                    scores[name] = q.freshness
                elif priority == "reliability":
                    scores[name] = q.reliability
                else:
                    scores[name] = q.quality_score
            else:
                scores[name] = 0.5
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return source_names[0] if source_names else ""
    
    def rank_data_quality(self, data_items: List[Dict]) -> List[Dict]:
        """
        对数据项进行质量排序
        """
        for item in data_items:
            item["_quality_score"] = self._calculate_quality_score(item)
        
        data_items.sort(key=lambda x: x.get("_quality_score", 0), reverse=True)
        return data_items
    
    def generate_data_quality_report(self, 
                                    source_stats: Dict[str, Dict]) -> str:
        """
        生成数据质量报告
        """
        try:
            if self.llm and source_stats:
                prompt = f"""请基于以下数据源统计生成数据质量报告：

{json.dumps(source_stats, ensure_ascii=False, indent=2)}

请提供：
1. 整体数据质量评估
2. 各数据源对比分析
3. 改进建议"""
                
                return str(self.llm.generate(  # type: ignore[return-value]
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=500
                ))
            else:
                return self._fallback_report(source_stats)
                
        except Exception as e:
            logger.warning(f"Report generation failed: {e}")
            return self._fallback_report(source_stats)
    
    def record_source_performance(self, source_name: str, 
                                 success: bool, 
                                 latency: float,
                                 data_quality: Optional[float] = None) -> None:
        """
        记录数据源性能
        """
        if source_name not in self.source_stats:
            self.source_stats[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_latency": 0.0,
                "avg_quality": 0.0,
                "last_used": None
            }
        
        stats = self.source_stats[source_name]
        if success:
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1
        
        stats["total_latency"] += latency
        if data_quality is not None:
            total = stats["success_count"] + stats["failure_count"]
            stats["avg_quality"] = (stats["avg_quality"] * (total - 1) + data_quality) / total
        
        stats["last_used"] = datetime.now().isoformat()
    
    def get_reliability_score(self, source_name: str) -> float:
        """
        获取数据源可靠性分数
        """
        if source_name not in self.source_stats:
            return 0.7
        
        stats = self.source_stats[source_name]
        total = stats["success_count"] + stats["failure_count"]
        if total == 0:
            return 0.7
        
        return stats["success_count"] / total  # type: ignore[no-any-return]
    
    def _format_data(self, data: Any) -> str:
        """格式化数据"""
        if isinstance(data, str):
            return data
        return json.dumps(data, ensure_ascii=False)
    
    def _get_system_prompt(self) -> str:
        return """你是一个专业的数据源质量评估专家。
请客观评估数据源的：
1. 数据准确性
2. 时效性
3. 完整性
4. 可靠性
请以JSON格式返回结果。"""
    
    def _build_evaluation_prompt(self, source_name: str, 
                                 data: str, 
                                 context: Optional[Dict]) -> str:
        context_str = f"\n上下文: {json.dumps(context, ensure_ascii=False)}" if context else ""
        
        return f"""请评估以下数据源质量：

数据源名称: {source_name}
数据内容:
{data[:1000]}
{context_str}

请以JSON格式返回：
{{
  "quality_score": 0.8,
  "reliability": 0.9,
  "freshness": 0.7,
  "accuracy": 0.8,
  "recommendations": ["建议1", "建议2"]
}}"""
    
    def _parse_quality_response(self, source_name: str, 
                                response: str) -> DataSourceQuality:
        """解析质量评估响应"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return DataSourceQuality(
                    source_name=source_name,
                    quality_score=data.get("quality_score", 0.5),
                    reliability=data.get("reliability", 0.5),
                    freshness=data.get("freshness", 0.5),
                    accuracy=data.get("accuracy", 0.5),
                    recommendations=data.get("recommendations", []),
                    last_evaluated=datetime.now().isoformat()
                )
        except Exception:
            pass
        
        return self._fallback_evaluation(source_name, {})
    
    def _fallback_evaluation(self, source_name: str, 
                            data: Any) -> DataSourceQuality:
        """降级评估方法"""
        return DataSourceQuality(
            source_name=source_name,
            quality_score=0.7,
            reliability=0.7,
            freshness=0.7,
            accuracy=0.7,
            recommendations=["需要更多数据进行评估"],
            last_evaluated=datetime.now().isoformat()
        )
    
    def _calculate_quality_score(self, item: Dict) -> float:
        """计算数据项质量分数"""
        score = 0.5
        
        completeness = 1.0
        for key, value in item.items():
            if value in [None, "", [], {}]:
                completeness -= 0.1
        
        score += completeness * 0.3
        
        if "timestamp" in item or "date" in item:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _fallback_report(self, source_stats: Dict[str, Dict]) -> str:
        """降级报告方法"""
        report = ["数据质量报告", "=" * 40]
        for name, stats in source_stats.items():
            total = stats.get("success_count", 0) + stats.get("failure_count", 0)
            report.append(f"{name}: {total}次调用, 平均质量: {stats.get('avg_quality', 0):.2f}")
        return "\n".join(report)


# 全局实例
LLM_DATA_MANAGER = LLMDataManager()

__all__ = ["LLMDataManager", "LLM_DATA_MANAGER", "DataSourceQuality"]
