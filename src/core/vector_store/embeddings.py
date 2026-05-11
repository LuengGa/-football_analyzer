"""
向量化工具 - 文本到向量
=========================
"""

import hashlib
import logging
from typing import List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    文本向量化生成器

    支持:
    - 本地嵌入 (基于TF-IDF)
    - LLM嵌入 (如果可用)
    """

    def __init__(self, model: str = "local"):
        self.model = model
        self._vocab: dict = {}
        self._idf: dict = {}

    def generate(self, text: str) -> List[float]:
        if not text:
            return [0.0] * 128

        if self.model == "local":
            return self._local_embedding(text)
        else:
            return self._simple_hash_embedding(text)

    def _local_embedding(self, text: str) -> List[float]:
        import re
        tokens = re.findall(r'\w+', text.lower())

        if not self._vocab:
            self._init_vocab()

        vector = [0.0] * 128
        for token in tokens:
            if token in self._vocab:
                idx = self._vocab[token] % 128
                vector[idx] += 1.0

        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def _simple_hash_embedding(self, text: str) -> List[float]:
        import struct
        hash_bytes = hashlib.md5(text.encode()).digest()
        values = list(struct.unpack('32f', hash_bytes + b'\x00' * (128 - 32) * 4))[:128]
        return values

    def _init_vocab(self) -> None:
        common_words = [
            "match", "team", "win", "lose", "draw", "goal", "score", "half",
            "league", "season", "home", "away", "player", "coach", "stadium",
            "football", "soccer", "betting", "odds", "prediction", "analysis",
            "premier", "laliga", "serie", "bundesliga", "ligue", "champions",
            "europa", "cup", "final", "semi", "quarter", "group", "table",
        ]
        self._vocab = {word: i for i, word in enumerate(common_words)}


EMBEDDING_GENERATOR = EmbeddingGenerator()


def embed_text(text: str, generator: Optional[EmbeddingGenerator] = None) -> List[float]:
    gen = generator or EMBEDDING_GENERATOR
    return gen.generate(text)


def embed_match_context(
    home_team: str,
    away_team: str,
    league: str,
    odds: dict = None
) -> List[float]:
    context = f"{home_team} vs {away_team} in {league}"
    if odds:
        odds_str = " ".join([f"{k}:{v}" for k, v in odds.items()])
        context += f" odds {odds_str}"

    return embed_text(context)


def embed_team_context(team: str, recent_results: List[str] = None) -> List[float]:
    context = team
    if recent_results:
        context += " " + " ".join(recent_results)

    return embed_text(context)
