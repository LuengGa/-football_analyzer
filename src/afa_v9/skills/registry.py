"""
AFA Skill Registry v1 — 基于 agentskills.io 标准
==================================================

技能分类：
- data: 数据获取类
- analysis: 分析计算类
- risk: 风控识别类
- execution: 投注执行类
- memory: 记忆检索类

技能元数据：
- id: 唯一标识符
- name: 技能名称
- description: 技能描述
- category: 技能分类
- tags: 技能标签
- version: 技能版本
- deprecated: 是否废弃
- requires_approval: 是否需要人工审批
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class SkillCategory(Enum):
    DATA = "data"           # 数据获取
    ANALYSIS = "analysis"   # 分析计算
    RISK = "risk"           # 风控识别
    EXECUTION = "execution" # 投注执行
    MEMORY = "memory"       # 记忆检索
    INTEL = "intel"         # 情报收集


@dataclass
class SkillMetadata:
    id: str
    name: str
    description: str
    category: SkillCategory
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    deprecated: bool = False
    requires_approval: bool = False
    examples: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "tags": self.tags,
            "version": self.version,
            "deprecated": self.deprecated,
            "requires_approval": self.requires_approval,
            "examples": self.examples,
            "related_skills": self.related_skills,
        }


@dataclass
class SkillDefinition:
    metadata: SkillMetadata
    parameters_schema: Dict[str, Any]
    executor: Optional[Callable] = None
    adapter: Optional[Callable] = None  # 用于适配旧版工具

    def to_openai(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "parameters": self.parameters_schema,
            }
        }

    def to_agentskills(self) -> Dict[str, Any]:
        return {
            "skill": self.metadata.to_dict(),
            "schema": self.parameters_schema,
        }


class SkillRegistry:
    _instance = None
    _skills: Dict[str, SkillDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, skill: SkillDefinition) -> None:
        if skill.metadata.deprecated:
            return
        self._skills[skill.metadata.id] = skill

    def get(self, skill_id: str) -> Optional[SkillDefinition]:
        return self._skills.get(skill_id)

    def get_by_name(self, name: str) -> Optional[SkillDefinition]:
        for skill in self._skills.values():
            if skill.metadata.name == name:
                return skill
        return None

    def list_by_category(self, category: SkillCategory) -> List[SkillDefinition]:
        return [s for s in self._skills.values() if s.metadata.category == category]

    def search(self, query: str) -> List[SkillDefinition]:
        query_lower = query.lower()
        results = []
        for skill in self._skills.values():
            if (query_lower in skill.metadata.name.lower() or
                query_lower in skill.metadata.description.lower() or
                any(query_lower in tag.lower() for tag in skill.metadata.tags)):
                results.append(skill)
        return results

    def get_all(self) -> List[SkillDefinition]:
        return list(self._skills.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [s.to_openai() for s in self._skills.values()]

    def export_agentskills(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "registry": "afa_skills",
            "skills": [s.to_agentskills() for s in self._skills.values()],
        }

    def export_markdown(self) -> str:
        lines = ["# AFA Skill Registry\n"]
        for category in SkillCategory:
            skills = self.list_by_category(category)
            if skills:
                lines.append(f"\n## {category.value.upper()}\n")
                for s in skills:
                    lines.append(f"- **{s.metadata.name}**: {s.metadata.description}")
        return "\n".join(lines)


def create_skill_from_tool_registry(
    name: str,
    description: str,
    category: SkillCategory,
    tags: List[str],
    schema: Dict[str, Any],
    executor: Callable,
    requires_approval: bool = False,
) -> SkillDefinition:
    return SkillDefinition(
        metadata=SkillMetadata(
            id=name,
            name=name,
            description=description,
            category=category,
            tags=tags,
            requires_approval=requires_approval,
        ),
        parameters_schema=schema,
        executor=executor,
    )
