"""
AFA Evolution Engine — 自进化系统
================================

Hermes Agent风格的自进化能力：
- 7阶段进化流程
- 技能自动生成与优化
- 模式识别与假说验证
- 经验积累与学习闭环
"""

from typing import Any, Optional, List, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EvolutionPhase(str, Enum):
    OBSERVATION = "observation"      # 观察阶段
    ANALYSIS = "analysis"            # 分析阶段
    HYPOTHESIS = "hypothesis"       # 假说阶段
    EXPERIMENT = "experiment"       # 实验阶段
    VALIDATION = "validation"       # 验证阶段
    INTEGRATION = "integration"     # 整合阶段
    CONSOLIDATION = "consolidation" # 巩固阶段


class OutcomeType(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    PARTIAL = "partial"


@dataclass
class Experience:
    """经验条目"""
    id: str
    context: Dict[str, Any]
    action: str
    outcome: OutcomeType
    metrics: Dict[str, float]
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "context": self.context,
            "action": self.action,
            "outcome": self.outcome.value if isinstance(self.outcome, Enum) else self.outcome,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "tags": self.tags,
            "learnings": self.learnings,
        }


@dataclass
class EvolvedSkill:
    """进化后的技能"""
    id: str
    name: str
    description: str
    code: str = ""
    effectiveness: float = 0.0
    usage_count: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    avg_profit: float = 0.0
    roi: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    source: str = "manual"
    confidence: float = 0.5

    def record_usage(self, success: bool, profit: float = 0.0) -> None:
        self.usage_count += 1
        self.last_used = datetime.now()
        if success:
            self.success_count += 1
            self.last_success = datetime.now()
        self.success_rate = self.success_count / self.usage_count if self.usage_count > 0 else 0
        self.avg_profit = (self.avg_profit * (self.usage_count - 1) + profit) / self.usage_count if self.usage_count > 0 else profit
        self.roi = self.avg_profit

        recency = 1.0 if self.last_success and (datetime.now() - self.last_success).days < 7 else 0.5
        consistency = min(1.0, self.success_rate * 1.2)
        self.effectiveness = self.success_rate * 0.5 + consistency * 0.3 + recency * 0.2

        if self.usage_count > 10:
            self.confidence = min(0.95, 0.5 + self.success_rate * 0.4)

    def is_stale(self, days: int = 30) -> bool:
        if not self.last_used:
            return (datetime.now() - self.created_at).days > days
        return (datetime.now() - self.last_used).days > days


@dataclass
class Pattern:
    """发现的模式"""
    id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    expected_outcome: str
    confidence: float
    support_count: int
    success_rate: float
    discovered_at: datetime
    validated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conditions": self.conditions,
            "expected_outcome": self.expected_outcome,
            "confidence": self.confidence,
            "support_count": self.support_count,
            "success_rate": self.success_rate,
            "discovered_at": self.discovered_at.isoformat() if isinstance(self.discovered_at, datetime) else self.discovered_at,
            "validated": self.validated,
        }


@dataclass
class Hypothesis:
    """待验证的假说"""
    id: str
    description: str
    hypothesis_type: str
    conditions: Dict[str, Any]
    predicted_effect: str
    evidence: List[str] = field(default_factory=list)
    status: str = "pending"
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)


class EvolutionEngine:
    """
    自进化引擎 - Hermes Agent风格

    7阶段进化流程：
    1. OBSERVATION - 观察阶段
    2. ANALYSIS - 分析阶段
    3. HYPOTHESIS - 假说阶段
    4. EXPERIMENT - 实验阶段
    5. VALIDATION - 验证阶段
    6. INTEGRATION - 整合阶段
    7. CONSOLIDATION - 巩固阶段
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.current_phase = EvolutionPhase.OBSERVATION
        self.experiences: List[Experience] = []
        self.skills: Dict[str, EvolvedSkill] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.evolution_log: List[Dict] = []

        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            storage_path = str(project_root / "data" / "evolution")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _get_storage_file(self, name: str) -> Path:
        return self.storage_path / f"{name}.json"

    def _load_state(self) -> None:
        try:
            for attr, filename in [
                ("experiences", "experiences"),
                ("skills", "skills"),
                ("patterns", "patterns"),
                ("hypotheses", "hypotheses"),
            ]:
                path = self._get_storage_file(filename)
                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if attr == "experiences":
                            self.experiences = [
                                Experience(
                                    id=e["id"],
                                    context=e["context"],
                                    action=e["action"],
                                    outcome=OutcomeType(e["outcome"]) if isinstance(e.get("outcome"), str) else e.get("outcome", OutcomeType.NEUTRAL),
                                    metrics=e.get("metrics", {}),
                                    timestamp=datetime.fromisoformat(e["timestamp"]) if isinstance(e.get("timestamp"), str) else datetime.now(),
                                    tags=e.get("tags", []),
                                    learnings=e.get("learnings", []),
                                )
                                for e in data
                            ]
                        elif attr == "skills":
                            for s in data.values():
                                self.skills[s["id"]] = EvolvedSkill(**s)
                        elif attr == "patterns":
                            for p in data.values():
                                self.patterns[p["id"]] = Pattern(**p)
                        elif attr == "hypotheses":
                            for h in data.values():
                                self.hypotheses[h["id"]] = Hypothesis(**h)
            logger.info(f"Evolution state loaded: {len(self.experiences)} experiences, {len(self.skills)} skills")
        except Exception as e:
            logger.warning(f"Failed to load evolution state: {e}")

    def _save_state(self, attr: str) -> None:
        try:
            filename_map = {
                "experiences": "experiences",
                "skills": "skills",
                "patterns": "patterns",
                "hypotheses": "hypotheses",
            }
            path = self._get_storage_file(filename_map.get(attr, attr))

            data: Any = None
            if attr == "experiences":
                data = [e.to_dict() for e in self.experiences[-1000:]]
            elif attr == "skills":
                data = {k: vars(v) for k, v in self.skills.items()}
            elif attr == "patterns":
                data = {k: v.to_dict() for k, v in self.patterns.items()}
            elif attr == "hypotheses":
                data = {k: vars(v) for k, v in self.hypotheses.items()}
            else:
                return

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Failed to save {attr}: {e}")

    def record_experience(
        self,
        context: Dict[str, Any],
        action: str,
        outcome: OutcomeType,
        metrics: Optional[Dict[str, float]] = None,
        tags: Optional[List[str]] = None,
    ) -> Experience:
        """记录经验"""
        exp_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.experiences)}"
        experience = Experience(
            id=exp_id,
            context=context,
            action=action,
            outcome=outcome,
            metrics=metrics or {},
            timestamp=datetime.now(),
            tags=tags or [],
        )
        self.experiences.append(experience)
        if len(self.experiences) > 1000:
            self.experiences = self.experiences[-500:]
        self._save_state("experiences")
        self._log_event("experience_recorded", {"id": exp_id, "outcome": outcome.value if isinstance(outcome, Enum) else outcome})
        return experience

    def create_skill(
        self,
        name: str,
        description: str,
        code: str = "",
        tags: Optional[List[str]] = None,
        source: str = "manual",
    ) -> EvolvedSkill:
        """创建新技能"""
        skill_id = f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        skill = EvolvedSkill(
            id=skill_id,
            name=name,
            description=description,
            code=code,
            tags=tags or [],
            source=source,
        )
        self.skills[skill_id] = skill
        self._save_state("skills")
        self._log_event("skill_created", {"id": skill_id, "name": name, "source": source})
        return skill

    def apply_skill(self, skill_id: str, success: bool, profit: float = 0.0) -> None:
        """应用技能并记录结果"""
        if skill_id in self.skills:
            self.skills[skill_id].record_usage(success, profit)
            self._save_state("skills")

    def generate_hypothesis(
        self,
        description: str,
        hypothesis_type: str,
        conditions: Dict[str, Any],
        predicted_effect: str,
    ) -> Hypothesis:
        """生成假说"""
        hyp_id = f"hyp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        hypothesis = Hypothesis(
            id=hyp_id,
            description=description,
            hypothesis_type=hypothesis_type,
            conditions=conditions,
            predicted_effect=predicted_effect,
            evidence=[],
        )
        self.hypotheses[hyp_id] = hypothesis
        self._save_state("hypotheses")
        return hypothesis

    def _log_event(self, event: str, data: Dict) -> None:
        self.evolution_log.append({
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase.value,
        })

    def analyze_patterns(self) -> Dict[str, Any]:
        """分析模式 - ANALYSIS阶段"""
        self.current_phase = EvolutionPhase.ANALYSIS

        if len(self.experiences) < 10:
            return {"patterns_found": 0, "message": "Insufficient data for pattern analysis"}

        success_exp = [e for e in self.experiences if e.outcome == OutcomeType.SUCCESS]
        success_rate = len(success_exp) / len(self.experiences) if self.experiences else 0

        leagues = {}
        for exp in self.experiences:
            league = exp.context.get("league", "unknown")
            if league not in leagues:
                leagues[league] = {"success": 0, "total": 0}
            leagues[league]["total"] += 1
            if exp.outcome == OutcomeType.SUCCESS:
                leagues[league]["success"] += 1

        league_rates = {
            league: data["success"] / data["total"] if data["total"] > 0 else 0
            for league, data in leagues.items()
        }

        patterns_found = []
        for league, rate in league_rates.items():
            if rate > 0.6 and leagues[league]["total"] >= 5:
                pattern_id = f"pattern_league_{league}_{datetime.now().strftime('%Y%m%d')}"
                pattern = Pattern(
                    id=pattern_id,
                    name=f"{league} League Pattern",
                    description=f"Success rate in {league} is {rate:.1%}",
                    conditions={"league": league, "min_rate": 0.6},
                    expected_outcome=f"{rate:.1%} success rate",
                    confidence=min(0.9, rate),
                    support_count=leagues[league]["total"],
                    success_rate=rate,
                    discovered_at=datetime.now(),
                    validated=True,
                )
                self.patterns[pattern_id] = pattern
                patterns_found.append(pattern.to_dict())

        self._save_state("patterns")
        self._log_event("patterns_analyzed", {"patterns_found": len(patterns_found)})

        return {
            "patterns_found": len(patterns_found),
            "overall_success_rate": success_rate,
            "league_rates": league_rates,
            "patterns": patterns_found,
        }

    def run_experiment(self, hypothesis_id: str) -> Dict[str, Any]:
        """运行实验 - EXPERIMENT阶段"""
        self.current_phase = EvolutionPhase.EXPERIMENT
        hypothesis = self.hypotheses.get(hypothesis_id)
        if not hypothesis:
            return {"error": "Hypothesis not found"}

        hypothesis.status = "testing"
        conditions = hypothesis.conditions

        matching_exp = []
        for exp in self.experiences[-100:]:
            match = True
            for key, value in conditions.items():
                if exp.context.get(key) != value:
                    match = False
                    break
            if match:
                matching_exp.append(exp)

        if len(matching_exp) < 3:
            hypothesis.evidence.append(f"Insufficient matching experiences: {len(matching_exp)}")
            hypothesis.confidence = 0.3
            return {"status": "insufficient_data", "matching_count": len(matching_exp)}

        success_count = sum(1 for e in matching_exp if e.outcome == OutcomeType.SUCCESS)
        observed_rate = success_count / len(matching_exp)

        hypothesis.evidence.append(f"Observed success rate: {observed_rate:.1%} ({len(matching_exp)} samples)")
        hypothesis.confidence = min(0.9, observed_rate)
        hypothesis.status = "validated" if len(matching_exp) >= 10 else "pending"

        if hypothesis.confidence > 0.7:
            skill = self.create_skill(
                name=f"Pattern: {hypothesis.description[:50]}",
                description=hypothesis.description,
                tags=["auto-generated", hypothesis.hypothesis_type],
                source="hypothesis",
            )
            hypothesis.evidence.append(f"Skill created: {skill.id}")

        self._save_state("hypotheses")
        self._save_state("skills")

        return {
            "status": hypothesis.status,
            "observed_rate": observed_rate,
            "matching_count": len(matching_exp),
            "confidence": hypothesis.confidence,
        }

    def evolve(self) -> Dict[str, Any]:
        """执行完整进化周期"""
        self.current_phase = EvolutionPhase.OBSERVATION

        pattern_analysis = self.analyze_patterns()

        self.current_phase = EvolutionPhase.HYPOTHESIS
        new_hypotheses = []
        for league, rate in pattern_analysis.get("league_rates", {}).items():
            if rate > 0.55:
                hyp = self.generate_hypothesis(
                    description=f"{league} teams perform better than expected",
                    hypothesis_type="league_performance",
                    conditions={"league": league},
                    predicted_effect="Higher win rate than baseline",
                )
                new_hypotheses.append(hyp.id)

        self.current_phase = EvolutionPhase.EXPERIMENT
        experiment_results = []
        for hyp_id in new_hypotheses[:3]:
            result = self.run_experiment(hyp_id)
            experiment_results.append({"hypothesis_id": hyp_id, "result": result})

        self.current_phase = EvolutionPhase.VALIDATION
        self.current_phase = EvolutionPhase.INTEGRATION

        performance = self.evaluate_performance()

        self.current_phase = EvolutionPhase.CONSOLIDATION

        stale_skills = [s for s in self.skills.values() if s.is_stale()]
        for skill in stale_skills:
            skill.effectiveness *= 0.9

        self._save_state("skills")

        evolution_result = {
            "phase": self.current_phase.value,
            "pattern_analysis": pattern_analysis,
            "new_hypotheses": len(new_hypotheses),
            "experiment_results": experiment_results,
            "performance": performance,
            "stale_skills_pruned": len(stale_skills),
        }

        self._log_event("evolution_complete", evolution_result)
        return evolution_result

    def evaluate_performance(self) -> Dict[str, float]:
        """评估当前性能"""
        if not self.skills:
            return {
                "overall_effectiveness": 0.0,
                "avg_success_rate": 0.0,
                "total_skills": 0,
                "active_skills": 0,
                "avg_roi": 0.0,
            }

        active = [s for s in self.skills.values() if s.usage_count > 0]
        return {
            "overall_effectiveness": sum(s.effectiveness for s in active) / len(active) if active else 0,
            "avg_success_rate": sum(s.success_rate for s in active) / len(active) if active else 0,
            "total_skills": len(self.skills),
            "active_skills": len(active),
            "avg_roi": sum(s.roi for s in active) / len(active) if active else 0,
        }

    def get_best_skills(self, count: int = 5) -> List[EvolvedSkill]:
        """获取最佳技能"""
        return sorted(self.skills.values(), key=lambda s: s.effectiveness, reverse=True)[:count]

    def get_active_patterns(self) -> List[Pattern]:
        """获取活跃模式"""
        return [p for p in self.patterns.values() if p.validated]

    def get_evolution_report(self) -> str:
        """生成进化报告"""
        performance = self.evaluate_performance()
        best_skills = self.get_best_skills(5)
        patterns = self.get_active_patterns()

        report = f"""# Self-Evolution Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Phase: {self.current_phase.value}

## Performance Metrics
- Overall Effectiveness: {performance['overall_effectiveness']:.1%}
- Average Success Rate: {performance['avg_success_rate']:.1%}
- Average ROI: {performance['avg_roi']:.2f}%
- Total Skills: {performance['total_skills']}
- Active Skills: {performance['active_skills']}

## Top Skills (by effectiveness)
"""
        for skill in best_skills:
            status = "🟢" if skill.effectiveness > 0.6 else "🟡" if skill.effectiveness > 0.4 else "🔴"
            report += f"{status} {skill.name}: {skill.effectiveness:.1%} | {skill.usage_count} uses | ROI: {skill.roi:.1%}\n"

        report += f"""
## Validated Patterns ({len(patterns)})
"""
        for pattern in patterns[:5]:
            report += f"- {pattern.name}: {pattern.confidence:.0%} confidence | {pattern.support_count} samples\n"

        report += f"""
## Statistics
- Total Experiences: {len(self.experiences)}
- Active Hypotheses: {len([h for h in self.hypotheses.values() if h.status == 'pending'])}
- Evolution Events: {len(self.evolution_log)}
"""
        return report

    def reset(self) -> None:
        """重置进化状态"""
        self.experiences.clear()
        self.skills.clear()
        self.patterns.clear()
        self.hypotheses.clear()
        self.evolution_log.clear()
        for attr in ["experiences", "skills", "patterns", "hypotheses"]:
            self._save_state(attr)
        logger.info("Evolution state reset")


EVOLUTION_ENGINE = EvolutionEngine()

from .data_accumulator import EvolutionDataAccumulator

__all__ = [
    "EvolutionPhase",
    "OutcomeType",
    "Experience",
    "EvolvedSkill",
    "Pattern",
    "Hypothesis",
    "EvolutionEngine",
    "EVOLUTION_ENGINE",
    "EvolutionDataAccumulator",
]
