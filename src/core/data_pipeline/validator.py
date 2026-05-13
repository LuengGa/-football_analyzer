"""
数据验证器 - 确保数据质量
==========================
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict[str, Any]] = None


class FieldValidator:
    """字段验证器"""

    @staticmethod
    def validate_odds(odds: Any, field_name: str = "odds") -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if odds is None:
            errors.append(f"{field_name} is None")
            return ValidationResult(False, errors, warnings)

        if isinstance(odds, dict):
            cleaned = {}
            for key, value in odds.items():
                if isinstance(value, (int, float)) and value > 0:
                    cleaned[key] = float(value)
                elif value is None:
                    warnings.append(f"{key} is None")
                else:
                    errors.append(f"{key} has invalid type: {type(value)}")

            if not cleaned:
                errors.append("No valid odds values")
                return ValidationResult(False, errors, warnings)

            return ValidationResult(True, errors, warnings, {"odds": cleaned})

        elif isinstance(odds, (int, float)):
            if odds <= 0:
                errors.append(f"Odds must be positive, got {odds}")
                return ValidationResult(False, errors, warnings)

            return ValidationResult(True, errors, warnings, {"odds": float(odds)})

        else:
            errors.append(f"Invalid odds type: {type(odds)}")
            return ValidationResult(False, errors, warnings)

    @staticmethod
    def validate_team_name(name: Any, field_name: str = "team") -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not name:
            errors.append(f"{field_name} name is empty")
            return ValidationResult(False, errors, warnings)

        name_str = str(name).strip()

        if len(name_str) < 2:
            errors.append(f"{field_name} name too short: {name_str}")
            return ValidationResult(False, errors, warnings)

        invalid_chars = ["<", ">", "{", "}", "|", "^"]
        for char in invalid_chars:
            if char in name_str:
                warnings.append(f"{field_name} contains special char: {char}")

        return ValidationResult(True, errors, warnings, {field_name: name_str})

    @staticmethod
    def validate_league(league: Any) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not league:
            warnings.append("League is empty")
            return ValidationResult(True, errors, warnings, {"league": "Unknown"})

        league_str = str(league).strip()

        known_leagues = [
            "premier league", "la liga", "serie a", "bundesliga",
            "ligue 1", "champions league", "europa league"
        ]

        league_lower = league_str.lower()
        if league_lower not in known_leagues:
            warnings.append(f"Unknown league: {league_str}")

        return ValidationResult(True, errors, warnings, {"league": league_str})

    @staticmethod
    def validate_match_id(match_id: Any) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not match_id:
            errors.append("Match ID is empty")
            return ValidationResult(False, errors, warnings)

        match_str = str(match_id).strip()

        if len(match_str) < 3:
            errors.append(f"Match ID too short: {match_str}")
            return ValidationResult(False, errors, warnings)

        return ValidationResult(True, errors, warnings, {"match_id": match_str})

    @staticmethod
    def validate_score(score: Any) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if score is None:
            warnings.append("Score is None (match may not have started)")
            return ValidationResult(True, errors, warnings, {"score": None})

        if isinstance(score, str):
            try:
                parts = score.replace("-", ":").split(":")
                score = {"home": int(parts[0].strip()), "away": int(parts[1].strip())}
            except Exception:
                errors.append(f"Invalid score format: {score}")
                return ValidationResult(False, errors, warnings)

        if isinstance(score, dict):
            home = score.get("home")
            away = score.get("away")

            if home is not None and not isinstance(home, int):
                errors.append(f"Home score must be int: {home}")
            if away is not None and not isinstance(away, int):
                errors.append(f"Away score must be int: {away}")

            if errors:
                return ValidationResult(False, errors, warnings)

            return ValidationResult(True, errors, warnings, {"score": score})

        errors.append(f"Invalid score type: {type(score)}")
        return ValidationResult(False, errors, warnings)


class MatchDataValidator:
    """比赛数据验证器"""

    def __init__(self, level: ValidationLevel = ValidationLevel.NORMAL):
        self.level = level

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        errors = []
        warnings = []
        cleaned = {}

        if not isinstance(data, dict):
            return ValidationResult(False, ["Data is not a dictionary"], warnings)

        if "match_id" in data or "id" in data:
            match_id = data.get("match_id") or data.get("id")
            result = FieldValidator.validate_match_id(match_id)
            errors.extend([f"match_id: {e}" for e in result.errors])
            warnings.extend([f"match_id: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)

        if "home_team" in data or "home" in data:
            home = data.get("home_team") or data.get("home")
            result = FieldValidator.validate_team_name(home, "home_team")
            errors.extend([f"home_team: {e}" for e in result.errors])
            warnings.extend([f"home_team: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)

        if "away_team" in data or "away" in data:
            away = data.get("away_team") or data.get("away")
            result = FieldValidator.validate_team_name(away, "away_team")
            errors.extend([f"away_team: {e}" for e in result.errors])
            warnings.extend([f"away_team: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)

        if "odds" in data:
            result = FieldValidator.validate_odds(data["odds"])
            errors.extend([f"odds: {e}" for e in result.errors])
            warnings.extend([f"odds: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)
            elif self.level == ValidationLevel.STRICT:
                pass
            else:
                cleaned["odds"] = data["odds"]

        if "league" in data:
            result = FieldValidator.validate_league(data["league"])
            warnings.extend([f"league: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)
            else:
                cleaned["league"] = data["league"]

        if "score" in data:
            result = FieldValidator.validate_score(data["score"])
            errors.extend([f"score: {e}" for e in result.errors])
            warnings.extend([f"score: {w}" for w in result.warnings])
            if result.cleaned_data:
                cleaned.update(result.cleaned_data)
            else:
                cleaned["score"] = data.get("score")

        for key, value in data.items():
            if key not in cleaned:
                cleaned[key] = value

        is_valid = len(errors) == 0 if self.level == ValidationLevel.STRICT else True

        return ValidationResult(is_valid, errors, warnings, cleaned)


class OddsValidator:
    """赔率数据验证器"""

    @staticmethod
    def validate_odds_format(odds_data: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        cleaned = {}

        required_fields = ["home_win", "draw", "away_win"]
        found_fields: List[str] = []

        if "odds" in odds_data:
            odds = odds_data["odds"]
        else:
            odds = odds_data

        if isinstance(odds, dict):
            for field in required_fields:
                if field in odds:
                    found_fields.append(field)
                    value = odds[field]
                    if isinstance(value, (int, float)) and 1.0 <= value <= 100.0:
                        cleaned[field] = float(value)
                    else:
                        warnings.append(f"{field} value out of range: {value}")

            missing = set(required_fields) - set(found_fields)
            if missing:
                warnings.append(f"Missing odds fields: {missing}")

        valid = len(errors) == 0 and len(found_fields) >= 2

        return ValidationResult(valid, errors, warnings, {"odds": cleaned})

    @staticmethod
    def check_odds_consistency(odds: Dict[str, float]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not odds:
            return ValidationResult(False, ["No odds data"], warnings)

        values = list(odds.values())

        if not values:
            return ValidationResult(False, ["Empty odds"], warnings)

        implied_probs = [1.0 / v for v in values if v > 0]
        total_implied = sum(implied_probs)

        if total_implied > 1.05:
            errors.append(f"Odds imply probability > 100%: {total_implied:.2%}")
        elif total_implied > 1.01:
            warnings.append(f"High bookmaker margin: {(total_implied - 1) * 100:.1f}%")

        if min(values) < 1.01:
            errors.append("Minimum odds too low")

        if max(values) > 100:
            warnings.append("Maximum odds unusually high")

        valid = len(errors) == 0

        return ValidationResult(valid, errors, warnings, odds)
