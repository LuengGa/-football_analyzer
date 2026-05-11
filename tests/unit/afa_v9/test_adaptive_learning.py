"""
Test cases for AdaptiveLearningLoop - 自适应学习回路测试
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.afa_v9.agents import ADAPTIVE_LEARNING, AdaptiveLearningLoop


def test_adaptive_learning_initialization():
    """测试自适应学习初始化"""
    learning = AdaptiveLearningLoop()
    assert learning is not None
    assert hasattr(learning, "bet_results")
    assert hasattr(learning, "current_parameters")
    assert "kelly_multiplier" in learning.current_parameters


def test_record_bet_result():
    """测试记录投注结果"""
    learning = AdaptiveLearningLoop()

    result = learning.record_bet_result(
        bet_id="test_bet_001",
        match_id="match_001",
        home_team="Man City",
        away_team="Arsenal",
        league="EPL",
        bet_type="home_win",
        odds=1.85,
        stake=100.0,
        actual_result="home_win",
        profit=85.0,
    )

    assert result.bet_id == "test_bet_001"
    assert result.profit == 85.0
    assert result.roi == 85.0
    assert len(learning.bet_results) >= 1


def test_self_assessment():
    """测试自我评估"""
    learning = AdaptiveLearningLoop()

    # 先记录一些投注结果
    for i in range(5):
        learning.record_bet_result(
            bet_id=f"test_bet_{i:03d}",
            match_id=f"match_{i:03d}",
            home_team=f"Team {i}",
            away_team=f"Team {i+1}",
            league="EPL",
            bet_type="home_win",
            odds=1.8,
            stake=100.0,
            actual_result="home_win" if i < 3 else "away_win",
            profit=80.0 if i < 3 else -100.0,
        )

    assessment = learning.self_assessment()

    assert "overall_assessment" in assessment
    assert "win_rate" in assessment
    assert "recommendations" in assessment


def test_get_learning_report():
    """测试获取学习报告"""
    learning = AdaptiveLearningLoop()

    report = learning.get_learning_report()

    assert "overview" in report
    assert "trending" in report
    assert "insights_count" in report
    assert "self_assessment" in report


def test_parameter_initialization():
    """测试参数初始化"""
    learning = AdaptiveLearningLoop()

    params = learning.current_parameters
    assert "kelly_multiplier" in params
    assert "confidence_threshold" in params
    assert "max_exposure" in params
    assert params["kelly_multiplier"] >= 0.1
    assert params["kelly_multiplier"] <= 2.0


def test_reset_learning():
    """测试重置学习"""
    learning = AdaptiveLearningLoop()

    # 记录一些数据
    learning.record_bet_result(
        "reset_test", "match_test", "A", "B", "EPL", "home_win", 1.8, 100, "home_win", 80
    )

    assert len(learning.bet_results) > 0

    # 重置
    learning.reset_learning()

    assert len(learning.bet_results) == 0
    assert len(learning.parameter_history) == 0


def test_stats_calculation():
    """测试统计数据计算"""
    learning = AdaptiveLearningLoop()
    learning.reset_learning()

    # 记录赢和输的投注
    learning.record_bet_result(
        "stats_1", "m1", "A", "B", "EPL", "home_win", 1.8, 100, "home_win", 80
    )
    learning.record_bet_result(
        "stats_2", "m2", "C", "D", "EPL", "home_win", 1.8, 100, "away_win", -100
    )
    learning.record_bet_result(
        "stats_3", "m3", "E", "F", "EPL", "home_win", 1.8, 100, "home_win", 80
    )

    assert learning.stats["total_bets"] == 3
    assert learning.stats["wins"] == 2
    assert learning.stats["losses"] == 1


def test_adaptive_learning_singleton():
    """测试单例模式"""
    from src.afa_v9.agents.adaptive_learning import ADAPTIVE_LEARNING as al1
    from src.afa_v9.agents.adaptive_learning import ADAPTIVE_LEARNING as al2

    assert al1 is al2


def test_integrated_workflow():
    """测试完整工作流"""
    learning = AdaptiveLearningLoop()
    learning.reset_learning()

    # 模拟真实使用场景
    for i in range(15):
        learning.record_bet_result(
            bet_id=f"bet_{i}",
            match_id=f"match_{i}",
            home_team=f"Home {i}",
            away_team=f"Away {i}",
            league="EPL",
            bet_type="home_win",
            odds=1.75,
            stake=100.0,
            actual_result="home_win" if i % 3 != 0 else "away_win",
            profit=75.0 if i % 3 != 0 else -100.0,
        )

    # 获取报告
    report = learning.get_learning_report()

    assert report["overview"]["total_bets"] == 15
    assert report["insights_count"] >= 0
