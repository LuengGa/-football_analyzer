import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.afa_v9.memory import (
    MEMORY_INSTANCE,
    BM25Search,
    EpisodicMemory,
    Memory,
    SemanticMemory,
    UnifiedMemory,
    WorkingMemory,
)


def test_working_memory():
    wm = WorkingMemory()
    wm.store("test_key", "test_value", importance=0.8)

    result = wm.recall("test_key")
    assert result == "test_value"


def test_episodic_memory():
    em = EpisodicMemory()
    episode_id = em.store_episode(
        event_type="test_event",
        content={"data": "test"},
        outcome="success",
    )

    assert episode_id.startswith("ep_")
    recent = em.get_recent_episodes(5)
    assert len(recent) >= 1


def test_semantic_memory():
    sm = SemanticMemory()
    sm.store_knowledge("capital", "London")
    sm.add_concept("geography")

    assert sm.recall_knowledge("capital") == "London"
    assert "geography" in sm.get_concepts()


def test_bm25_search():
    search = BM25Search()
    search.index_document("doc1", "Manchester City wins the match")
    search.index_document("doc2", "Arsenal loses to Chelsea")
    search.index_document("doc3", "Liverpool draws with Manchester")

    results = search.search("Manchester")
    assert len(results) >= 2


def test_unified_memory():
    um = UnifiedMemory()
    um.store("premier_league", "Top tier English football", importance=0.9)

    results = um.search("football")
    assert len(results) >= 1


def test_memory_singleton():
    assert MEMORY_INSTANCE is not None
    assert isinstance(MEMORY_INSTANCE, Memory)


def test_store_interaction():
    memory = Memory()
    memory.store_interaction("test_interaction", {"result": "success"})

    results = memory.search_memory("test_interaction")
    assert isinstance(results, list)
