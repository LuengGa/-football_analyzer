"""Vector Store Module"""
from .store import (
    VectorStore,
    SimpleVectorStore,
    ChromaVectorStore,
    VectorStoreFactory,
    get_default_store,
)
from .embeddings import (
    EmbeddingGenerator,
    EMBEDDING_GENERATOR,
    embed_text,
    embed_match_context,
    embed_team_context,
)

__all__ = [
    "VectorStore",
    "SimpleVectorStore",
    "ChromaVectorStore",
    "VectorStoreFactory",
    "get_default_store",
    "EmbeddingGenerator",
    "EMBEDDING_GENERATOR",
    "embed_text",
    "embed_match_context",
    "embed_team_context",
]
