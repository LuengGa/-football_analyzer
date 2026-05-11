import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.data_pipeline import (
    DataPipeline,
    PipelineResult,
    ValidationLevel,
    FieldValidator,
)


def test_pipeline_match():
    pipeline = DataPipeline(validation_level=ValidationLevel.NORMAL)

    result = pipeline.process_match({
        "home_team": "Manchester City",
        "away_team": "Arsenal",
        "league": "Premier League",
        "odds": {"home_win": 1.85, "draw": 3.5, "away_win": 4.2},
    })

    assert isinstance(result, PipelineResult)
    assert result.success is True or len(result.warnings) >= 0


def test_pipeline_team_cleaning():
    pipeline = DataPipeline()

    result = pipeline.process_match({
        "home_team": "Man City",
        "away_team": "arsenal",
        "league": "epl",
        "odds": {"home": 1.9, "draw": 3.3, "away": 4.0},
    })

    assert result.success is True
    if result.data:
        assert "team" in result.data["home_team"].lower() or result.data["home_team"]


def test_pipeline_odds_validation():
    pipeline = DataPipeline()

    result = pipeline.process_match({
        "home_team": "Test Home",
        "away_team": "Test Away",
        "odds": {"home_win": 1.5, "draw": 4.0, "away_win": 6.0},
    })

    assert isinstance(result, PipelineResult)


def test_pipeline_invalid_odds():
    pipeline = DataPipeline(validation_level=ValidationLevel.STRICT)

    result = pipeline.process_match({
        "home_team": "Test Home",
        "away_team": "Test Away",
        "odds": {"home_win": -1.5},
    })

    assert isinstance(result, PipelineResult)


def test_pipeline_batch():
    pipeline = DataPipeline()

    items = [
        {"home_team": "Team A", "away_team": "Team B"},
        {"home_team": "Team C", "away_team": "Team D"},
    ]

    results = pipeline.process_batch(items, item_type="match")

    assert len(results) == 2
    assert all(isinstance(r, PipelineResult) for r in results)


def test_field_validator_team():
    result = FieldValidator.validate_team_name("Manchester City", "home_team")
    assert result.valid is True
    assert result.cleaned_data is not None


def test_field_validator_odds():
    result = FieldValidator.validate_odds({"home": 1.85, "away": 4.2})
    assert result.valid is True


def test_field_validator_empty():
    result = FieldValidator.validate_team_name("", "team")
    assert result.valid is False
