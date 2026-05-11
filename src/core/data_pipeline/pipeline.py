"""
数据处理管道 - 验证+清洗一体化
=================================
"""

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .validator import MatchDataValidator, OddsValidator, ValidationResult, ValidationLevel
from .cleaner import MatchDataCleaner

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    success: bool
    data: Optional[Dict[str, Any]]
    validation_result: ValidationResult
    errors: list
    warnings: list


class DataPipeline:
    """
    数据处理管道

    流程: 原始数据 → 清洗 → 验证 → 标准化输出

    使用方式:
        pipeline = DataPipeline()

        result = pipeline.process_match({
            "home": "Man City",
            "away": "Arsenal",
            "odds": {"home": 1.85, "draw": 3.5, "away": 4.2}
        })

        if result.success:
            print(result.data)
    """

    def __init__(
        self,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
        strict_cleaning: bool = True
    ):
        self.validator = MatchDataValidator(level=validation_level)
        self.cleaner = MatchDataCleaner()
        self.strict_cleaning = strict_cleaning

    def process_match(self, raw_data: Dict[str, Any]) -> PipelineResult:
        """
        处理比赛数据

        1. 清洗数据
        2. 验证数据
        3. 返回标准化结果
        """
        errors = []
        warnings = []

        try:
            cleaned = self.cleaner.clean(raw_data)
        except Exception as e:
            logger.error(f"Cleaning failed: {e}")
            return PipelineResult(
                success=False,
                data=None,
                validation_result=ValidationResult(False, [str(e)], []),
                errors=[str(e)],
                warnings=[],
            )

        validation = self.validator.validate(cleaned)
        errors.extend(validation.errors)
        warnings.extend(validation.warnings)

        success = len(errors) == 0 if self.strict_cleaning else True

        return PipelineResult(
            success=success,
            data=validation.cleaned_data or cleaned,
            validation_result=validation,
            errors=errors,
            warnings=warnings,
        )

    def process_odds(self, raw_odds: Dict[str, Any]) -> PipelineResult:
        """
        处理赔率数据

        1. 验证赔率格式
        2. 检查赔率一致性
        3. 返回标准化结果
        """
        errors = []
        warnings = []

        format_validation = OddsValidator.validate_odds_format(raw_odds)
        errors.extend(format_validation.errors)
        warnings.extend(format_validation.warnings)

        odds_data = format_validation.cleaned_data or raw_odds
        odds = odds_data.get("odds", {})

        if odds:
            consistency = OddsValidator.check_odds_consistency(odds)
            errors.extend(consistency.errors)
            warnings.extend(consistency.warnings)

            if consistency.cleaned_data:
                odds_data["odds"] = consistency.cleaned_data

        success = len(errors) == 0 if self.strict_cleaning else True

        return PipelineResult(
            success=success,
            data=odds_data,
            validation_result=format_validation,
            errors=errors,
            warnings=warnings,
        )

    def process_batch(self, items: list, item_type: str = "match") -> list[PipelineResult]:
        """
        批量处理数据

        item_type: "match" 或 "odds"
        """
        process_func = (
            self.process_match
            if item_type == "match"
            else self.process_odds
        )

        results = []
        for item in items:
            result = process_func(item)
            results.append(result)

        success_count = sum(1 for r in results if r.success)
        logger.info(f"Batch processing: {success_count}/{len(results)} succeeded")

        return results
