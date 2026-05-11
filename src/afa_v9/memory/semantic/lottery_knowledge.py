"""
彩票规则语义记忆模块

将官方规则转换为语义化的知识表示，支持自然语言查询。
规则来源：data/knowledge/jingcai-rules.json 和 data/knowledge/beidan-rules.json，
玩法规则：data/knowledge/jingcai/play_types/ 和 data/knowledge/beidan/play_types/
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class RuleChunk:
    """规则知识块 - 语义记忆的基本单元"""
    id: str
    content: str
    category: str  # jingcai, beidan, general
    play_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.9  # 规则非常重要
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "play_type": self.play_type,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RuleChunk":
        """从字典创建规则块"""
        created_at_str = data.get("created_at")
        try:
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
            else:
                created_at = datetime.now()
        except (ValueError, TypeError):
            created_at = datetime.now()
        
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            category=data.get("category", "general"),
            play_type=data.get("play_type"),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.9),
            created_at=created_at
        )


class LotterySemanticMemory:
    """
    彩票规则语义记忆系统

    从JSON文件读取官方规则，支持自然语言查询。
    """

    def __init__(self, knowledge_file: Optional[Path] = None):
        self._chunks: Dict[str, RuleChunk] = {}
        self._index: Dict[str, List[str]] = {}  # 关键词 -> chunk ids
        self._full_knowledge: Dict[str, Any] = {}
        
        if knowledge_file:
            self._initialize_from_single_file(knowledge_file)
        else:
            self._initialize_from_split_files()
            
        self._build_index()

    @staticmethod
    def _find_project_root() -> Path:
        """找到项目根目录"""
        current_path = Path(__file__).resolve()
        for parent in current_path.parents:
            if (parent / "pyproject.toml").exists() or (parent / "data").exists():
                return parent
        return current_path.parent.parent.parent.parent

    def _initialize_from_single_file(self, knowledge_file: Path):
        """从单个文件初始化"""
        if not knowledge_file.exists():
            raise FileNotFoundError(f"Knowledge file not found: {knowledge_file}")
        
        with open(knowledge_file, "r", encoding="utf-8") as f:
            self._full_knowledge = json.load(f)
        
        self._load_chunks_from_full_knowledge(self._full_knowledge)

    def _initialize_from_split_files(self):
        """从拆分的竞彩和北单文件初始化"""
        project_root = self._find_project_root()
        jingcai_file = project_root / "data" / "knowledge" / "jingcai-rules.json"
        beidan_file = project_root / "data" / "knowledge" / "beidan-rules.json"
        
        all_chunks = []
        
        # 尝试加载竞彩规则
        if jingcai_file.exists():
            with open(jingcai_file, "r", encoding="utf-8") as f:
                jingcai_data = json.load(f)
                if "knowledge_chunks" in jingcai_data:
                    all_chunks.extend(jingcai_data["knowledge_chunks"])
                self._full_knowledge["jingcai"] = jingcai_data
            
            # 加载竞彩的玩法文件
            jingcai_play_types_dir = project_root / "data" / "knowledge" / "jingcai" / "play_types"
            if jingcai_play_types_dir.exists():
                for play_type_file in jingcai_play_types_dir.glob("*.json"):
                    with open(play_type_file, "r", encoding="utf-8") as f:
                        play_type_data = json.load(f)
                        if "knowledge_chunk" in play_type_data:
                            all_chunks.append(play_type_data["knowledge_chunk"])
        
        # 尝试加载北单规则
        if beidan_file.exists():
            with open(beidan_file, "r", encoding="utf-8") as f:
                beidan_data = json.load(f)
                if "knowledge_chunks" in beidan_data:
                    all_chunks.extend(beidan_data["knowledge_chunks"])
                self._full_knowledge["beidan"] = beidan_data
            
            # 加载北单的玩法文件
            beidan_play_types_dir = project_root / "data" / "knowledge" / "beidan" / "play_types"
            if beidan_play_types_dir.exists():
                for play_type_file in beidan_play_types_dir.glob("*.json"):
                    with open(play_type_file, "r", encoding="utf-8") as f:
                        play_type_data = json.load(f)
                        if "knowledge_chunk" in play_type_data:
                            all_chunks.append(play_type_data["knowledge_chunk"])
        
        # 添加通用规则
        all_chunks.extend(self._get_general_rule_chunks())
        
        # 加载所有chunk
        for chunk_data in all_chunks:
            chunk = RuleChunk.from_dict(chunk_data)
            self._chunks[chunk.id] = chunk

    @staticmethod
    def _get_general_rule_chunks() -> List[Dict]:
        """获取通用规则知识块"""
        return [
            {
                "id": "general_tax_rules",
                "content": "中国体育彩票个人所得税规则：单注奖金≥1万元时，扣除20%的个人所得税。单注奖金<1万元时，免征个人所得税。",
                "category": "general",
                "play_type": None,
                "importance": 0.9
            },
            {
                "id": "general_match_time_rules",
                "content": "足球彩票竞猜的结果计算：均以全场90分钟（含伤停补时）的比赛结果为准，加时赛和点球大战的结果不计入。",
                "category": "general",
                "play_type": None,
                "importance": 0.9
            }
        ]

    def _load_chunks_from_full_knowledge(self, knowledge: Dict):
        """从完整知识中加载chunks（兼容旧格式）"""
        if "knowledge_chunks" in knowledge:
            for chunk_data in knowledge["knowledge_chunks"]:
                chunk = RuleChunk.from_dict(chunk_data)
                self._chunks[chunk.id] = chunk
        elif "lotteries" in knowledge:
            # 处理旧格式的合并文件
            jingcai = knowledge["lotteries"].get("jingcai")
            if jingcai and "knowledge_chunks" in jingcai:
                for chunk_data in jingcai["knowledge_chunks"]:
                    chunk = RuleChunk.from_dict(chunk_data)
                    self._chunks[chunk.id] = chunk
            
            beidan = knowledge["lotteries"].get("beidan")
            if beidan and "knowledge_chunks" in beidan:
                for chunk_data in beidan["knowledge_chunks"]:
                    chunk = RuleChunk.from_dict(chunk_data)
                    self._chunks[chunk.id] = chunk
        
        # 总是添加通用规则
        for chunk_data in self._get_general_rule_chunks():
            chunk = RuleChunk.from_dict(chunk_data)
            self._chunks[chunk.id] = chunk

    def _build_index(self):
        """构建关键词索引"""
        for chunk_id, chunk in self._chunks.items():
            keywords = self._extract_keywords(chunk.content)
            keywords.append(chunk.category)
            if chunk.play_type:
                keywords.append(chunk.play_type)
            
            for keyword in keywords:
                keyword = keyword.lower()
                if keyword not in self._index:
                    self._index[keyword] = []
                if chunk_id not in self._index[keyword]:
                    self._index[keyword].append(chunk_id)

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词（简化版）"""
        keywords = []
        important_terms = [
            "竞彩", "北单", "北京单场", "胜平负", "让球", "比分",
            "总进球", "半全场", "混合过关", "上下单双", "胜负过关",
            "返奖率", "串关", "赔率", "SP值", "奖金", "封顶",
            "英超", "西甲", "意甲", "德甲", "法甲", "欧冠",
            "联赛", "玩法", "个税", "所得税", "让球", "税率",
            "M串1", "M串N", "自由过关", "容错", "2×1", "3×1",
            "4×1", "3×4", "4×5", "4×11", "组合", "过关方式"
        ]
        for term in important_terms:
            if term in text:
                keywords.append(term)
        return keywords

    def query(self, query: str, top_k: int = 5) -> List[Dict]:
        """自然语言查询规则"""
        query_keywords = self._extract_keywords(query)
        query_lower = query.lower()
        scores: Dict[str, float] = {}

        for chunk_id, chunk in self._chunks.items():
            score = 0.0
            for keyword in query_keywords:
                if keyword in chunk.content:
                    score += 1.0
            if "竞彩" in query_lower and chunk.category == "jingcai":
                score += 2.0
            if "北单" in query_lower and chunk.category == "beidan":
                score += 2.0
            if chunk.play_type and chunk.play_type in query:
                score += 3.0
            for word in query_lower.split():
                if word in chunk.content.lower():
                    score += 0.5
            scores[chunk_id] = score

        sorted_chunks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            {**self._chunks[chunk_id].to_dict(), "score": score}
            for chunk_id, score in sorted_chunks
            if score > 0
        ]

    def get_all_chunks(self) -> List[Dict]:
        """获取所有知识块"""
        return [chunk.to_dict() for chunk in self._chunks.values()]

    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """获取指定知识块"""
        chunk = self._chunks.get(chunk_id)
        return chunk.to_dict() if chunk else None

    def get_chunks_by_category(self, category: str) -> List[Dict]:
        """按分类获取知识块"""
        return [
            chunk.to_dict()
            for chunk in self._chunks.values()
            if chunk.category == category
        ]

    def get_full_knowledge(self) -> Dict[str, Any]:
        """获取完整的知识JSON"""
        return self._full_knowledge


_LOTTERY_SEMANTIC_MEMORY: Optional[LotterySemanticMemory] = None


def get_lottery_semantic_memory() -> LotterySemanticMemory:
    """获取彩票规则语义记忆单例"""
    global _LOTTERY_SEMANTIC_MEMORY
    if _LOTTERY_SEMANTIC_MEMORY is None:
        _LOTTERY_SEMANTIC_MEMORY = LotterySemanticMemory()
    return _LOTTERY_SEMANTIC_MEMORY
