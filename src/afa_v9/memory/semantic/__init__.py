"""
语义记忆模块

提供彩票规则的语义化知识表示，支持自然语言查询。
"""

from .lottery_knowledge import (
    LotterySemanticMemory,
    RuleChunk,
    get_lottery_semantic_memory,
)

__all__ = [
    "LotterySemanticMemory",
    "RuleChunk",
    "get_lottery_semantic_memory",
]
