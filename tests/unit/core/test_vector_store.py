import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.vector_store import (
    VectorStoreFactory,
    embed_match_context,
    embed_team_context,
    embed_text,
    get_default_store,
)


def test_vector_store_factory():
    store = VectorStoreFactory.create("test_collection")
    assert store is not None
    assert hasattr(store, "add")
    assert hasattr(store, "search")


def test_default_store():
    store = get_default_store()
    assert store is not None


def test_add_and_search():
    store = VectorStoreFactory.create("test_search")

    test_id = "test_doc_1"
    vector = embed_text("Manchester City vs Arsenal Premier League")
    metadata = {
        "title": "Test Match",
        "type": "match_analysis",
        "league": "Premier League",
    }

    store.add(test_id, vector, metadata)

    query = embed_text("Premier League football")
    results = store.search(query, top_k=1)

    assert len(results) >= 1
    assert results[0]["id"] == test_id


def test_embed_text():
    vec1 = embed_text("Manchester City wins the match")
    vec2 = embed_text("Manchester City loses the match")

    assert len(vec1) == 128
    assert len(vec2) == 128


def test_embed_match_context():
    vec = embed_match_context(
        home_team="Manchester City",
        away_team="Arsenal",
        league="Premier League",
        odds={"home": 1.8, "draw": 3.5, "away": 4.2},
    )

    assert len(vec) == 128


def test_embed_team_context():
    vec = embed_team_context(team="Liverpool", recent_results=["W", "W", "D", "L", "W"])

    assert len(vec) == 128


def test_store_count():
    from src.core.vector_store import SimpleVectorStore

    store = SimpleVectorStore("test_count_persistent")
    initial_count = store.count()

    for i in range(3):
        test_id = f"count_test_{i}"
        vector = embed_text(f"Test document {i}")
        store.add(test_id, vector, {"index": i})

    assert store.count() >= initial_count + 3
