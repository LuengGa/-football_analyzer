"""
pre_filter compatibility layer
从 calculations/pre_filter 导入，保持向后兼容
"""
from src.calculations.quant.pre_filter import MatchPreFilter

pre_filter_matches = MatchPreFilter().filter_matches

__all__ = ["MatchPreFilter", "pre_filter_matches"]
