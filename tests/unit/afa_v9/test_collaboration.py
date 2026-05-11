"""
Test cases for AgentCollaborationManager - 多Agent协作框架测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.afa_v9.agents import (
    COLLABORATION_MANAGER,
    AgentCollaborationManager,
)


def test_collaboration_manager_initialization():
    """测试协作管理器初始化"""
    manager = AgentCollaborationManager()
    assert manager is not None
    assert hasattr(manager, "agents")
    assert "Scout" in manager.agents
    assert "Quant" in manager.agents


def test_send_message():
    """测试Agent间消息发送"""
    manager = AgentCollaborationManager()
    
    message = manager.send_message(
        sender="Scout",
        receiver="Quant",
        content="发现伤情",
        message_type="info",
    )
    
    assert message.sender == "Scout"
    assert message.receiver == "Quant"
    assert message.content == "发现伤情"


def test_broadcast_message():
    """测试广播消息"""
    manager = AgentCollaborationManager()
    
    messages = manager.broadcast_message(
        sender="Trader",
        content="决策已做出",
        receivers=["Quant", "Risk", "Auditor"],
    )
    
    assert len(messages) == 3


def test_task_assignment():
    """测试任务分配"""
    manager = AgentCollaborationManager()
    
    task = manager.assign_task(
        task_type="quantitative_analysis",
        task_description="数据模型分析",
        priority=8,
    )
    
    assert task.assigned_agent == "Quant"
    assert task.priority == 8


def test_collective_decision():
    """测试集体决策"""
    manager = AgentCollaborationManager()
    
    decision = manager.collective_decision(
        topic="投资策略选择",
        options=["保守", "激进"],
    )
    
    assert decision.topic == "投资策略选择"
    assert len(decision.participants) > 0
    assert hasattr(decision, "final_decision")
    assert hasattr(decision, "consensus_reached")


def test_get_collaboration_stats():
    """测试获取协作统计"""
    manager = AgentCollaborationManager()
    
    # 先发送一些消息生成统计
    manager.send_message("Scout", "Quant", "test 1")
    manager.send_message("Quant", "Risk", "test 2")
    
    stats = manager.get_collaboration_stats()
    
    assert "total_messages" in stats
    assert "pending_tasks" in stats
    assert "total_decisions" in stats
    assert "consensus_rate" in stats


def test_collaboration_manager_singleton():
    """测试单例模式"""
    from src.afa_v9.agents.collaboration import COLLABORATION_MANAGER as cm1
    from src.afa_v9.agents.collaboration import COLLABORATION_MANAGER as cm2
    
    assert cm1 is cm2
