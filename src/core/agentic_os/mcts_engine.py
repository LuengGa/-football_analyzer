"""
标准 MCTS (Monte Carlo Tree Search) 四阶段算法实现

职责：
- Selection: UCT选择策略遍历树
- Expansion: 扩展新节点
- Simulation: 随机模拟/rollout
- Backpropagation: 反向传播更新统计信息

用于足球比赛的多分支战术推演和概率评估
"""
import math
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """节点类型"""
    ROOT = "root"
    CHANCE = "chance"  # 机会节点（随机事件）
    DECISION = "decision"  # 决策节点


@dataclass
class MCTSNode:
    """MCTS 搜索树节点"""
    state: Dict[str, Any]  # 游戏状态
    parent: Optional['MCTSNode'] = None
    children: List['MCTSNode'] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0  # 累计价值
    node_type: NodeType = NodeType.DECISION
    action: Optional[str] = None  # 导致此状态的动作
    untried_actions: List[str] = field(default_factory=list)
    
    def is_fully_expanded(self) -> bool:
        """检查节点是否完全展开"""
        return len(self.untried_actions) == 0
    
    def best_child(self, exploration_constant: float = 1.414) -> 'MCTSNode':
        """使用UCT公式选择最佳子节点"""
        if not self.children:
            raise ValueError("No children available")
        
        uct_values = []
        for child in self.children:
            if child.visits == 0 or self.visits == 0:
                uct = float('inf')
            else:
                exploitation = child.value / child.visits
                exploration = exploration_constant * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                uct = exploitation + exploration
            uct_values.append(uct)
        
        max_uct = max(uct_values)
        best_children = [
            child for child, uct in zip(self.children, uct_values)
            if uct == max_uct
        ]
        return random.choice(best_children)
    
    def update(self, reward: float):
        """更新节点统计信息"""
        self.visits += 1
        self.value += reward


class FootballGameState:
    """
    足球比赛游戏状态表示
    
    包含比分、时间、球员状态、战术配置等
    """
    
    def __init__(self, match_context: Dict[str, Any]):
        self.home_team = match_context.get("home_team", "")
        self.away_team = match_context.get("away_team", "")
        self.home_score = match_context.get("home_score", 0)
        self.away_score = match_context.get("away_score", 0)
        self.minute = match_context.get("minute", 0)
        self.home_xg = match_context.get("home_xg", 0.0)
        self.away_xg = match_context.get("away_xg", 0.0)
        self.home_momentum = match_context.get("home_momentum", 0.5)
        self.away_momentum = match_context.get("away_momentum", 0.5)
        self.home_cards = match_context.get("home_cards", 0)
        self.away_cards = match_context.get("away_cards", 0)
        self.home_injuries = match_context.get("home_injuries", [])
        self.away_injuries = match_context.get("away_injuries", [])
        
        # 赔率信息
        self.odds_home_win = match_context.get("odds_home_win", 2.0)
        self.odds_draw = match_context.get("odds_draw", 3.4)
        self.odds_away_win = match_context.get("odds_away_win", 3.5)
    
    def copy(self) -> 'FootballGameState':
        """创建状态副本"""
        new_state = FootballGameState({
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "minute": self.minute,
            "home_xg": self.home_xg,
            "away_xg": self.away_xg,
            "home_momentum": self.home_momentum,
            "away_momentum": self.away_momentum,
            "home_cards": self.home_cards,
            "away_cards": self.away_cards,
            "home_injuries": self.home_injuries.copy(),
            "away_injuries": self.away_injuries.copy(),
            "odds_home_win": self.odds_home_win,
            "odds_draw": self.odds_draw,
            "odds_away_win": self.odds_away_win,
        })
        return new_state
    
    def is_terminal(self) -> bool:
        """检查是否为终止状态（比赛结束）"""
        return bool(self.minute >= 90)
    
    def get_possible_actions(self) -> List[str]:
        """获取当前状态下可能的动作"""
        actions = []
        
        # 基本动作：进球、黄牌、红牌、换人等
        if self.home_momentum > 0.6:
            actions.append("home_goal")
        if self.away_momentum > 0.6:
            actions.append("away_goal")
        
        actions.append("no_goal")  # 无进球
        
        # 红牌可能性（如果已有黄牌或犯规多）
        if self.home_cards >= 3:
            actions.append("home_red_card")
        if self.away_cards >= 3:
            actions.append("away_red_card")
        
        # 受伤可能性
        if random.random() < 0.05:
            actions.append("home_injury")
        if random.random() < 0.05:
            actions.append("away_injury")
        
        return actions if actions else ["no_goal"]
    
    def apply_action(self, action: str) -> 'FootballGameState':
        """应用动作，返回新状态"""
        new_state = self.copy()
        new_state.minute += 5  # 每次模拟前进5分钟
        
        if action == "home_goal":
            new_state.home_score += 1
            new_state.home_xg += 0.7
            new_state.home_momentum = min(1.0, new_state.home_momentum + 0.1)
            new_state.away_momentum = max(0.0, new_state.away_momentum - 0.15)
        
        elif action == "away_goal":
            new_state.away_score += 1
            new_state.away_xg += 0.7
            new_state.away_momentum = min(1.0, new_state.away_momentum + 0.1)
            new_state.home_momentum = max(0.0, new_state.home_momentum - 0.15)
        
        elif action == "home_red_card":
            new_state.home_cards += 1
            new_state.home_momentum *= 0.7
            new_state.away_momentum *= 1.2
        
        elif action == "away_red_card":
            new_state.away_cards += 1
            new_state.away_momentum *= 0.7
            new_state.home_momentum *= 1.2
        
        elif action == "home_injury":
            new_state.home_momentum *= 0.85
        
        elif action == "away_injury":
            new_state.away_momentum *= 0.85
        
        # no_goal: 动量小幅波动
        else:
            new_state.home_momentum *= random.uniform(0.95, 1.05)
            new_state.away_momentum *= random.uniform(0.95, 1.05)
        
        return new_state
    
    def evaluate(self) -> float:
        """
        评估当前状态的期望价值
        
        Returns:
            float: 对主队的期望价值 [-1, 1]
        """
        if self.is_terminal():
            # 比赛结束，根据结果评分
            if self.home_score > self.away_score:
                return 1.0  # 主队胜
            elif self.home_score < self.away_score:
                return -1.0  # 客队胜
            else:
                return 0.0  # 平局
        
        # 非终止状态，基于xG差值和动量评估
        xg_diff = self.home_xg - self.away_xg
        momentum_diff = self.home_momentum - self.away_momentum
        
        # 加权评分
        score = 0.6 * math.tanh(xg_diff) + 0.4 * momentum_diff
        return max(-1.0, min(1.0, score))  # type: ignore[no-any-return]


class MCTS:
    """
    标准蒙特卡洛树搜索 (MCTS) 实现
    
    四阶段算法：
    1. Selection (选择): UCT策略选择子节点
    2. Expansion (扩展): 展开新节点
    3. Simulation (模拟): 随机rollout到终止状态
    4. Backpropagation (回溯): 更新路径上所有节点
    """
    
    def __init__(
        self,
        simulation_count: int = 1000,
        exploration_constant: float = 1.414,
        timeout_seconds: float = 5.0
    ):
        """
        初始化 MCTS
        
        Args:
            simulation_count: 模拟次数
            exploration_constant: UCT探索常数 (sqrt(2) ≈ 1.414)
            timeout_seconds: 搜索超时时间（秒）
        """
        self.simulation_count = simulation_count
        self.exploration_constant = exploration_constant
        self.timeout_seconds = timeout_seconds
        self.root: Optional[MCTSNode] = None
    
    def search(self, initial_state: FootballGameState) -> MCTSNode:
        """
        执行 MCTS 搜索
        
        Args:
            initial_state: 初始游戏状态
            
        Returns:
            MCTSNode: 根节点（包含搜索结果）
        """
        start_time = time.time()
        
        # 创建根节点
        self.root = MCTSNode(
            state=initial_state,  # type: ignore[arg-type]
            untried_actions=initial_state.get_possible_actions()  # type: ignore[union-attr]
        )
        
        print(f"   -> 🌳 [MCTS] 开始搜索 | 目标模拟次数: {self.simulation_count} | 超时: {self.timeout_seconds}s")
        
        iteration = 0
        while iteration < self.simulation_count:
            # 检查超时
            if time.time() - start_time > self.timeout_seconds:
                print(f"   -> ⏱️ [MCTS] 达到超时限制，停止搜索 (完成 {iteration} 次迭代)")
                break
            
            # Phase 1: Selection
            node = self._selection(self.root)
            
            # Phase 2: Expansion
            if not node.state.get("is_terminal", lambda: False)() and not node.is_fully_expanded():  # type: ignore[union-attr,operator]
                node = self._expansion(node)
            
            # Phase 3: Simulation
            reward = self._simulation(node.state)  # type: ignore[arg-type]
            
            # Phase 4: Backpropagation
            self._backpropagation(node, reward)
            
            iteration += 1
            
            # 每100次迭代输出进度
            if iteration % 100 == 0:
                elapsed = time.time() - start_time
                print(f"   -> 📊 [MCTS] 进度: {iteration}/{self.simulation_count} | 耗时: {elapsed:.2f}s")
        
        total_time = time.time() - start_time
        print(f"   -> ✅ [MCTS] 搜索完成 | 总迭代: {iteration} | 总耗时: {total_time:.2f}s")
        
        return self.root
    
    def _selection(self, node: MCTSNode) -> MCTSNode:
        """
        Phase 1: Selection - 使用UCT策略选择节点
        
        从根节点向下遍历，直到到达未完全展开的节点或叶节点
        """
        while node.children and node.is_fully_expanded():
            node = node.best_child(self.exploration_constant)
        return node
    
    def _expansion(self, node: MCTSNode) -> MCTSNode:
        """
        Phase 2: Expansion - 扩展新节点
        
        从未尝试的动作中选择一个，创建新的子节点
        """
        action = node.untried_actions.pop()  # type: ignore[union-attr]
        new_state = node.state.apply_action(action)  # type: ignore[union-attr,attr-defined]
        
        child_node = MCTSNode(
            state=new_state,
            parent=node,
            action=action,
            untried_actions=new_state.get_possible_actions()  # type: ignore[union-attr]
        )
        
        node.children.append(child_node)  # type: ignore[union-attr]
        return child_node
    
    def _simulation(self, state: FootballGameState) -> float:
        """
        Phase 3: Simulation - 随机模拟到终止状态
        
        从当前状态开始，随机选择动作直到游戏结束
        """
        current_state = state.copy()
        max_steps = 20  # 限制最大步数防止无限循环
        step = 0
        
        while not current_state.is_terminal() and step < max_steps:
            actions = current_state.get_possible_actions()
            if not actions:
                break
            
            # 随机选择动作（可以替换为更智能的策略）
            action = random.choice(actions)
            current_state = current_state.apply_action(action)
            step += 1
        
        # 返回最终状态的评估值
        return current_state.evaluate()
    
    def _backpropagation(self, node: MCTSNode, reward: float):
        """
        Phase 4: Backpropagation - 反向传播更新
        
        从叶节点向上更新路径上所有节点的统计信息
        """
        while node is not None:
            node.update(reward)
            node = node.parent  # type: ignore[assignment]
    
    def get_best_action(self) -> Tuple[str, MCTSNode]:
        """
        获取最佳动作（基于访问次数最多的子节点）
        
        Returns:
            Tuple[str, MCTSNode]: (最佳动作, 对应子节点)
        """
        if not self.root or not self.root.children:
            raise ValueError("MCTS search has not been performed yet")
        
        # 选择访问次数最多的子节点
        best_child = max(self.root.children, key=lambda c: c.visits)
        return best_child.action or "unknown", best_child
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        if not self.root:
            return {}
        
        stats = {
            "total_visits": self.root.visits,
            "num_children": len(self.root.children),
            "children_stats": []
        }
        
        for child in self.root.children:
            child_stats = {
                "action": child.action,
                "visits": child.visits,
                "avg_value": child.value / child.visits if child.visits > 0 else 0,
                "win_rate": child.value / child.visits if child.visits > 0 else 0
            }
            stats["children_stats"].append(child_stats)  # type: ignore[union-attr,attr-defined]
        
        return stats
    
    def print_tree(self, node: Optional[MCTSNode] = None, depth: int = 0, max_depth: int = 3):
        """打印搜索树结构（用于调试）"""
        if node is None:
            node = self.root
        
        if node is None or depth > max_depth:
            return
        
        indent = "  " * depth
        avg_value = node.value / node.visits if node.visits > 0 else 0
        
        print(f"{indent}[{node.action or 'ROOT'}] visits={node.visits}, avg_value={avg_value:.3f}")
        
        for child in node.children:
            self.print_tree(child, depth + 1, max_depth)


def run_mcts_analysis(match_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行 MCTS 分析并返回结果
    
    Args:
        match_context: 比赛上下文信息
        
    Returns:
        Dict: 分析结果，包含最佳动作、概率分布等
    """
    # 创建初始状态
    initial_state = FootballGameState(match_context)
    
    # 创建 MCTS 实例
    mcts = MCTS(
        simulation_count=1000,
        exploration_constant=1.414,
        timeout_seconds=5.0
    )
    
    # 执行搜索
    root = mcts.search(initial_state)
    
    # 获取最佳动作
    try:
        best_action, best_child = mcts.get_best_action()
    except ValueError:
        best_action = "no_goal"
        best_child = None
    
    # 获取统计信息
    stats = mcts.get_statistics()
    
    # 计算各结果概率
    home_win_prob = 0.0
    draw_prob = 0.0
    away_win_prob = 0.0
    
    if best_child:
        # 基于子节点的访问次数分布计算概率
        total_visits = sum(c.visits for c in root.children)
        for child in root.children:
            prob = child.visits / total_visits if total_visits > 0 else 0
            final_state = child.state
            
            if final_state.home_score > final_state.away_score:  # type: ignore[union-attr,attr-defined]
                home_win_prob += prob
            elif final_state.home_score < final_state.away_score:  # type: ignore[union-attr,attr-defined]
                away_win_prob += prob
            else:
                draw_prob += prob
    
    result = {
        "best_action": best_action,
        "home_win_probability": home_win_prob,
        "draw_probability": draw_prob,
        "away_win_probability": away_win_prob,
        "statistics": stats,
        "final_state": {
            "home_score": initial_state.home_score,  # type: ignore[union-attr,attr-defined]
            "away_score": initial_state.away_score,  # type: ignore[union-attr,attr-defined]
            "home_xg": initial_state.home_xg,
            "away_xg": initial_state.away_xg,
        }
    }
    
    return result


if __name__ == "__main__":
    # 测试示例
    test_context = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "home_score": 1,
        "away_score": 1,
        "minute": 70,
        "home_xg": 1.5,
        "away_xg": 1.2,
        "home_momentum": 0.7,
        "away_momentum": 0.5,
        "home_cards": 2,
        "away_cards": 1,
        "odds_home_win": 2.10,
        "odds_draw": 3.40,
        "odds_away_win": 3.50,
    }
    
    print("=" * 60)
    print("MCTS 四阶段算法测试")
    print("=" * 60)
    
    result = run_mcts_analysis(test_context)
    
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)
    print(f"最佳动作: {result['best_action']}")
    print(f"主胜概率: {result['home_win_probability']:.2%}")
    print(f"平局概率: {result['draw_probability']:.2%}")
    print(f"客胜概率: {result['away_win_probability']:.2%}")
    print(f"\n详细统计:")
    for child_stat in result['statistics'].get('children_stats', []):
        print(f"  - {child_stat['action']}: visits={child_stat['visits']}, "
              f"avg_value={child_stat['avg_value']:.3f}")
