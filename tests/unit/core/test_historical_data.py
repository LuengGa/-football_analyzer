import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.historical_data import (
    HISTORICAL_LOADER,
    HistoricalDataLoader,
    MatchRecord,
)


def test_loader_initialization():
    loader = HistoricalDataLoader()
    assert loader is not None
    assert loader.data_path.exists()


def test_load_metadata():
    loader = HistoricalDataLoader()
    metadata = loader.load_metadata()
    assert isinstance(metadata, dict)


def test_load_all():
    loader = HistoricalDataLoader()
    matches = loader.load_all()
    assert isinstance(matches, list)


def test_matches_have_required_fields():
    loader = HistoricalDataLoader()
    matches = loader.load_all()

    if matches:
        match = matches[0]
        assert hasattr(match, "match_id")
        assert hasattr(match, "home_team")
        assert hasattr(match, "away_team")
        assert hasattr(match, "date")
        assert hasattr(match, "result")


def test_get_matches_by_league():
    loader = HistoricalDataLoader()
    epl_matches = loader.get_matches_by_league("E0")
    assert isinstance(epl_matches, list)


def test_get_matches_by_team():
    loader = HistoricalDataLoader()
    city_matches = loader.get_matches_by_team("Manchester City")
    assert isinstance(city_matches, list)


def test_get_recent_matches():
    loader = HistoricalDataLoader()
    recent = loader.get_recent_matches(limit=10)
    assert len(recent) <= 10


def test_match_record_to_dict():
    loader = HistoricalDataLoader()
    matches = loader.load_all()

    if matches:
        match = matches[0]
        assert isinstance(match, MatchRecord)

        match_dict = match.to_dict()
        assert "home_team" in match_dict
        assert "away_team" in match_dict


def test_stats():
    loader = HistoricalDataLoader()
    stats = loader.get_stats()
    assert isinstance(stats, dict)
    assert "total_matches" in stats


def test_leagues_and_teams():
    loader = HistoricalDataLoader()
    leagues = loader.get_leagues()
    teams = loader.get_teams()

    assert isinstance(leagues, list)
    assert isinstance(teams, list)
    assert len(leagues) > 0
    assert len(teams) > 0
