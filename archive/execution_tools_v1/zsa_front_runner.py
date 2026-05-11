import time
from typing import Dict, Any
from src.tools.execution.betting_ledger import BettingLedger
from src.agents.grandmaster_router import GrandmasterRouter

class ZSAFrontRunner:
    """
    Zero-Shot Arbitrage (ZSA) 截胡执行器。
    监听 SocialNewsListener 的内存总线，一旦发现改变基本面的重大情报（如核心受伤），
    绕过所有慢速的 LangGraph 节点和复杂数学计算，直接向底层账本发起做空出票请求。
    """
    def __init__(self, listener=None):
        self.listener = listener
        self.ledger = BettingLedger()
        self.router = GrandmasterRouter()
        
        if listener:
            listener.register_callback(self.handle_extreme_news)
        
        self.live_markets = {}

    def register_market(self, team: str, match_id: str, opponent: str, odds: Dict[str, float], is_home: bool):
        self.live_markets[team] = {
            "match_id": match_id,
            "opponent": opponent,
            "odds": odds,
            "is_home": is_home
        }

    def handle_extreme_news(self, team: str, news: str, impact: float):
        print(f"\n🚨🚨🚨 [ZSA 截胡系统触发] 🚨🚨🚨")
        print(f"   -> 接收到极端情报: {team} | Impact: {impact}")
        print(f"   -> 准备进行内存总线阻断与极速执行...")
        
        market = self.live_markets.get(team)
        if not market:
            print(f"   -> ❌ 未找到 {team} 的走地盘口，取消截胡。")
            return
            
        start_t = time.perf_counter()
        
        if impact <= -0.8:
            target_selection = "away_win" if market["is_home"] else "home_win"
            target_team = market["opponent"]
            target_odds = market["odds"][target_selection]
            stake = 500.0
            
            print(f"   -> ⚡ 决策: {team} 遭遇重创，极速做空！买入 {target_team} 胜 (赔率 {target_odds})")
            
            res = self.ledger.execute_bet(
                agent_id="zsa_front_runner",
                match_id=market["match_id"],
                lottery_type="jingcai",
                selection=f"WDL_{target_selection}",
                odds=target_odds,
                stake=stake
            )
            
            end_t = time.perf_counter()
            latency = (end_t - start_t) * 1000
            
            if res.get("status") == "success":
                print(f"   -> ✅ [ZSA 截胡成功] 耗时: {latency:.2f}ms | 凭证: {res['ticket_code']} | 余额: ${res['remaining_balance']:.2f}")
                self.router.dispatch_matches({}, {f"WDL_{target_selection}": 0.99}, {"jingcai_odds": {f"WDL_{target_selection}": target_odds}})
            else:
                print(f"   -> ❌ [ZSA 截胡失败] 耗时: {latency:.2f}ms | 原因: {res.get('message')}")
