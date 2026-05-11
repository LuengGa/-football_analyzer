"""
AFA v9.0 多Agent协作框架 - 集体智慧与协作优化
====================================================

功能：
1. Agent间自然对话交流
2. 集体决策优化
3. 任务自动分配
4. 共识达成机制
5. 协作历史记录
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from . import (
    ALL_AGENTS,
    SCOUT_AGENT,
    QUANT_AGENT,
    MARKET_AGENT,
    RISK_AGENT,
    TRADER_AGENT,
    AUDITOR_AGENT,
    LOTTERY_ROUTER_AGENT,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Agent间消息"""
    sender: str
    receiver: str
    content: str
    message_type: str = "info"  # info, request, decision, feedback
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborativeDecision:
    """集体决策结果"""
    topic: str
    participants: List[str]
    final_decision: Dict[str, Any]
    vote_results: Dict[str, str]
    consensus_reached: bool
    reasoning: str
    timestamp: str


@dataclass
class TaskAssignment:
    """任务分配结果"""
    task_id: str
    task_type: str
    assigned_agent: str
    priority: int
    status: str = "pending"
    deadline: Optional[str] = None


class AgentCollaborationManager:
    """
    Agent协作管理器
    
    功能：
    - Agent间消息传递
    - 任务自动分配
    - 集体决策达成
    - 协作历史记录
    """

    def __init__(self):
        self.agents = {
            "Scout": SCOUT_AGENT,
            "Quant": QUANT_AGENT,
            "Market": MARKET_AGENT,
            "Risk": RISK_AGENT,
            "Trader": TRADER_AGENT,
            "Auditor": AUDITOR_AGENT,
            "LotteryRouter": LOTTERY_ROUTER_AGENT,
        }
        self.message_queue: List[AgentMessage] = []
        self.task_queue: List[TaskAssignment] = []
        self.decision_history: List[CollaborativeDecision] = []
        self.collaboration_logs: List[Dict] = []
        
        # 专家领域映射
        self.expertise_map = {
            "intelligence_gathering": ["Scout"],
            "quantitative_analysis": ["Quant"],
            "market_analysis": ["Market"],
            "risk_management": ["Risk"],
            "trading_decision": ["Trader"],
            "audit_review": ["Auditor"],
            "lottery_routing": ["LotteryRouter"],
            "general_decision": ["Trader", "Risk", "Auditor"],
        }
        
        # 初始化协作数据目录
        self._data_dir = Path(__file__).parent.parent.parent.parent / "data" / "collaboration"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🤝 Agent协作管理器初始化完成")

    def send_message(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "info",
        context: Optional[Dict] = None,
    ) -> AgentMessage:
        """发送Agent间消息"""
        message = AgentMessage(
            sender=sender,
            receiver=receiver,
            content=content,
            message_type=message_type,
            context=context or {},
        )
        self.message_queue.append(message)
        logger.info(f"💬 [{sender}] → [{receiver}]: {content[:50]}...")
        return message

    def broadcast_message(
        self,
        sender: str,
        content: str,
        receivers: Optional[List[str]] = None,
        context: Optional[Dict] = None,
    ) -> List[AgentMessage]:
        """广播消息到多个Agent"""
        receivers = receivers or list(self.agents.keys())
        messages = []
        for receiver in receivers:
            if receiver != sender:
                msg = self.send_message(sender, receiver, content, "broadcast", context)
                messages.append(msg)
        return messages

    def assign_task(
        self,
        task_type: str,
        task_description: str,
        priority: int = 5,
        specific_agent: Optional[str] = None,
    ) -> TaskAssignment:
        """
        自动分配任务给合适的Agent
        
        Args:
            task_type: 任务类型
            task_description: 任务描述
            priority: 优先级 (1-10)
            specific_agent: 指定Agent（可选）
        """
        # 确定合适的Agent
        if specific_agent and specific_agent in self.agents:
            assigned_agent = specific_agent
        else:
            expert_agents = self.expertise_map.get(task_type, ["Trader"])
            assigned_agent = expert_agents[0]
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assignment = TaskAssignment(
            task_id=task_id,
            task_type=task_type,
            assigned_agent=assigned_agent,
            priority=priority,
            status="pending",
        )
        
        self.task_queue.append(assignment)
        
        # 发送任务通知
        self.send_message(
            "CollaborationManager",
            assigned_agent,
            f"新任务分配: {task_description}",
            "task_assignment",
            {"task_id": task_id, "task_type": task_type, "priority": priority},
        )
        
        logger.info(f"📋 任务 {task_id} 分配给 [{assigned_agent}]")
        return assignment

    def collective_decision(
        self,
        topic: str,
        options: List[str],
        participants: Optional[List[str]] = None,
        context: Optional[Dict] = None,
    ) -> CollaborativeDecision:
        """
        集体决策 - Agent投票达成共识
        
        Args:
            topic: 决策主题
            options: 选项列表
            participants: 参与Agent（可选）
            context: 决策上下文
        """
        participants = participants or ["Quant", "Risk", "Trader", "Auditor"]
        
        print(f"\n{'='*60}")
        print(f"🤝 集体决策: {topic}")
        print(f"{'='*60}")
        print(f"参与Agent: {', '.join(participants)}")
        
        # 模拟投票
        vote_results = {}
        for agent in participants:
            # 简单决策逻辑 - 实际可使用LLM
            vote = options[0] if agent in ["Quant", "Trader"] else options[1]
            vote_results[agent] = vote
            print(f"   {agent} 投票: {vote}")
        
        # 计算共识
        option_counts = {}
        for vote in vote_results.values():
            option_counts[vote] = option_counts.get(vote, 0) + 1
        
        majority_option = max(option_counts.items(), key=lambda x: x[1])
        consensus_reached = majority_option[1] > len(participants) * 0.5
        
        final_decision = {
            "selected_option": majority_option[0],
            "vote_count": majority_option[1],
            "total_participants": len(participants),
        }
        
        decision = CollaborativeDecision(
            topic=topic,
            participants=participants,
            final_decision=final_decision,
            vote_results=vote_results,
            consensus_reached=consensus_reached,
            reasoning=f"集体投票: {majority_option[0]} 获得 {majority_option[1]} 票"
            + ("，达成共识" if consensus_reached else "，未达成共识"),
            timestamp=datetime.now().isoformat(),
        )
        
        self.decision_history.append(decision)
        
        print(f"\n决策结果: {decision.final_decision['selected_option']}")
        print(f"共识达成: {'✅ 是' if decision.consensus_reached else '❌ 否'}")
        
        return decision

    def collaborative_analysis(
        self,
        match_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        协作式比赛分析 - Agent间协同工作
        
        流程：
        1. LotteryRouter: 路由彩种
        2. Scout: 情报收集
        3. Quant: 量化分析
        4. Market: 市场分析
        5. Risk: 风险评估
        6. Trader: 最终决策
        7. Auditor: 审计复盘
        """
        print(f"\n{'='*70}")
        print(f"🏟️ AFA v9.0 Agent协作分析开始")
        print(f"{'='*70}")
        print(f"比赛: {match_data.get('home_team')} vs {match_data.get('away_team')}")
        print(f"联赛: {match_data.get('league')}")
        
        state = match_data.copy()
        
        # 1. 彩种路由
        print("\n[步骤 1/7] 彩种路由...")
        lottery_result = LOTTERY_ROUTER_AGENT.execute(state)
        state.update(lottery_result)
        
        # 2. 情报收集
        print("\n[步骤 2/7] 情报收集...")
        scout_result = SCOUT_AGENT.execute(state)
        state.update(scout_result)
        
        # 3. 量化分析
        print("\n[步骤 3/7] 量化分析...")
        quant_result = QUANT_AGENT.execute(state)
        state.update(quant_result)
        
        # 4. 市场分析
        print("\n[步骤 4/7] 市场分析...")
        market_result = MARKET_AGENT.execute(state)
        state.update(market_result)
        
        # 5. 风险评估
        print("\n[步骤 5/7] 风险评估...")
        risk_result = RISK_AGENT.execute(state)
        state.update(risk_result)
        
        # 6. 交易决策
        print("\n[步骤 6/7] 交易决策...")
        trader_result = TRADER_AGENT.execute(state)
        state.update(trader_result)
        
        # 7. 审计复盘
        print("\n[步骤 7/7] 审计复盘...")
        auditor_result = AUDITOR_AGENT.execute(state)
        state.update(auditor_result)
        
        print(f"\n{'='*70}")
        print("✅ Agent协作分析完成")
        print(f"{'='*70}")
        
        # 记录协作日志
        self._log_collaboration(state)
        
        return state

    def _log_collaboration(self, result: Dict) -> None:
        """记录协作过程"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "match": f"{result.get('home_team')} vs {result.get('away_team')}",
            "league": result.get("league"),
            "lottery_type": result.get("lottery_type"),
            "final_decision": result.get("trader_decision", {}),
        }
        self.collaboration_logs.append(log_entry)
        
        # 保存到文件
        log_file = self._data_dir / f"collab_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            logs = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            logs.append(log_entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"保存协作日志失败: {e}")

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """获取协作统计"""
        return {
            "total_messages": len(self.message_queue),
            "pending_tasks": sum(1 for t in self.task_queue if t.status == "pending"),
            "total_decisions": len(self.decision_history),
            "consensus_rate": (
                sum(1 for d in self.decision_history if d.consensus_reached)
                / len(self.decision_history)
                if self.decision_history
                else 0
            ),
            "agent_activity": {
                agent: sum(
                    1 for msg in self.message_queue if msg.sender == agent or msg.receiver == agent
                )
                for agent in self.agents.keys()
            },
        }


# 全局单例
COLLABORATION_MANAGER = AgentCollaborationManager()
