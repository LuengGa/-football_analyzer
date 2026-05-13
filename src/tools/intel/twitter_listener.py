"""
Twitter API 实时情报监听器

职责：
- 通过 Twitter API v2 流式获取足球相关新闻
- 支持关键词过滤（球队名称、球员名称）
- 与 SocialNewsListener 集成，提供毫秒级情报推送
"""
import os
import time
import threading
import json
from typing import Dict, List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("tweepy not installed. Twitter listener will use mock mode.")


class TwitterStreamListener:
    """
    Twitter 流式监听器 - ZSA 快轨数据源
    
    使用 Twitter API v2 filtered stream 实时捕获足球相关推文。
    当检测到重大新闻（核心球员受伤、红牌等）时，触发内存总线回调。
    """
    
    def __init__(self, use_mock: bool = None):
        env_mock = os.getenv("TWITTER_MOCK", "true").lower() in ("true", "1", "yes")
        self.use_mock = env_mock if use_mock is None else use_mock
        
        # Twitter API 配置
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        
        # 监控的球队列表（动态更新）
        self.watched_teams: List[str] = []
        self.watched_keywords: List[str] = [
            "injury", "red card", "suspended", "out of match",
            "hamstring", "ACL", "concussion", "starting lineup"
        ]
        
        # 内存缓存
        self._cache: Dict[str, dict] = {}
        self._cache_lock = threading.Lock()
        
        # 回调函数列表
        self._callbacks: List[Callable] = []
        
        # Stream 连接状态
        self._stream_running = False
        self._stream_thread: Optional[threading.Thread] = None
        
        # 初始化 Twitter Client
        self.client = None
        if not self.use_mock and TWEEPY_AVAILABLE:
            self._init_twitter_client()
    
    def _init_twitter_client(self):
        """初始化 Twitter API 客户端"""
        if not self.bearer_token:
            logger.warning("TWITTER_BEARER_TOKEN not set. Using mock mode.")
            self.use_mock = True
            return
        
        try:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
            logger.info("✓ Twitter API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            self.use_mock = True
    
    def register_callback(self, callback: Callable):
        """注册情报回调函数"""
        self._callbacks.append(callback)
    
    def add_watched_team(self, team_name: str):
        """添加监控球队"""
        if team_name not in self.watched_teams:
            self.watched_teams.append(team_name)
            logger.info(f"Added watched team: {team_name}")
    
    def start_streaming(self):
        """启动流式监听"""
        if self.use_mock:
            logger.info("Twitter listener running in MOCK mode")
            return
        
        if not self.client:
            logger.error("Twitter client not initialized")
            return
        
        self._stream_running = True
        self._stream_thread = threading.Thread(
            target=self._run_stream,
            daemon=True,
            name="TwitterStreamThread"
        )
        self._stream_thread.start()
        logger.info("✓ Twitter streaming started")
    
    def stop_streaming(self):
        """停止流式监听"""
        self._stream_running = False
        if self._stream_thread:
            self._stream_thread.join(timeout=5)
        logger.info("Twitter streaming stopped")
    
    def _run_stream(self):
        """运行 Twitter 流式连接（后台线程）"""
        try:
            # 构建过滤规则
            rules = self._build_filter_rules()
            
            # 清除旧规则
            existing_rules = self.client.get_filtered_stream_rules()
            if existing_rules.data:
                rule_ids = [rule.id for rule in existing_rules.data]
                self.client.delete_filtered_stream_rules(ids=rule_ids)
            
            # 添加新规则
            if rules:
                self.client.add_filtered_stream_rules(rules)
            
            # 开始流式监听
            for response in self.client.sampled_stream(
                expansions=["author_id", "entities"],
                tweet_fields=["created_at", "text", "lang"],
                user_fields=["username", "verified"]
            ):
                if not self._stream_running:
                    break
                
                if response.data:
                    self._process_tweet(response.data)
        
        except Exception as e:
            logger.error(f"Twitter stream error: {e}")
            # 尝试重连
            time.sleep(10)
            if self._stream_running:
                self._run_stream()
    
    def _build_filter_rules(self) -> List[dict]:
        """构建 Twitter 过滤规则"""
        rules = []
        
        # 为每个监控球队添加规则
        for team in self.watched_teams:
            rules.append({"value": f'"{team}" (injury OR "red card" OR suspended OR "out of")'})
        
        # 通用足球突发新闻规则
        rules.append({
            "value": '(football OR soccer) AND (breaking OR urgent) AND (injury OR "red card")'
        })
        
        return rules
    
    def _process_tweet(self, tweet):
        """处理接收到的推文"""
        try:
            text = tweet.text
            lang = getattr(tweet, 'lang', 'en')
            
            # 只处理英文推文
            if lang != 'en':
                return
            
            # 提取相关球队
            related_teams = self._extract_teams(text)
            
            if not related_teams:
                return
            
            # 缓存最新推文
            with self._cache_lock:
                for team in related_teams:
                    self._cache[team] = {
                        "timestamp": time.time(),
                        "team": team,
                        "news": text,
                        "source": "twitter_api",
                        "tweet_id": tweet.id,
                        "latency_ms": 0
                    }
            
            # 触发回调（由 SocialNewsListener 进行 xG 影响分析）
            for team in related_teams:
                self._fire_callbacks(team, text)
        
        except Exception as e:
            logger.error(f"Error processing tweet: {e}")
    
    def _extract_teams(self, text: str) -> List[str]:
        """从推文中提取相关球队名称"""
        found_teams = []
        text_lower = text.lower()
        
        for team in self.watched_teams:
            if team.lower() in text_lower:
                found_teams.append(team)
        
        return found_teams
    
    def _fire_callbacks(self, team: str, news: str):
        """触发情报回调"""
        for cb in self._callbacks:
            try:
                threading.Thread(
                    target=cb,
                    args=(team, news),
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def get_latest_news(self, team: str) -> Optional[dict]:
        """获取指定球队的最新推文"""
        with self._cache_lock:
            return self._cache.get(team)
    
    def _mock_tweet_generator(self):
        """Mock 推文生成器（用于测试）"""
        import random
        
        mock_tweets = [
            {
                "team": "Arsenal",
                "text": "BREAKING: Arsenal star striker suffers severe hamstring injury during warm-up and is out of the match.",
                "impact": -0.8
            },
            {
                "team": "Manchester City",
                "text": "Good news! Kevin De Bruyne returns to training ahead of schedule. Expected to start this weekend.",
                "impact": 0.3
            },
            {
                "team": "Liverpool",
                "text": "CONFIRMED: Virgil van Dijk receives red card in first half. Liverpool down to 10 men.",
                "impact": -0.7
            }
        ]
        
        while self._stream_running:
            tweet = random.choice(mock_tweets)
            with self._cache_lock:
                self._cache[tweet["team"]] = {
                    "timestamp": time.time(),
                    "team": tweet["team"],
                    "news": tweet["text"],
                    "source": "twitter_mock",
                    "latency_ms": random.randint(15, 80)
                }
            
            for cb in self._callbacks:
                try:
                    threading.Thread(
                        target=cb,
                        args=(tweet["team"], tweet["text"]),
                        daemon=True
                    ).start()
                except:
                    pass
            
            time.sleep(60)  # 每60秒生成一条mock推文


class BetfairWebSocketListener:
    """
    Betfair WebSocket 实时盘口监听器
    
    通过 Betfair Exchange API 订阅实时赔率变化。
    当检测到异常赔率波动时，立即触发 ZSA 截胡机制。
    """
    
    def __init__(self, use_mock: bool = None):
        env_mock = os.getenv("BETFAIR_MOCK", "true").lower() in ("true", "1", "yes")
        self.use_mock = env_mock if use_mock is None else use_mock
        
        # Betfair API 配置
        self.app_key = os.getenv("BETFAIR_APP_KEY")
        self.session_token = os.getenv("BETFAIR_SESSION_TOKEN")
        
        # 监控的市场
        self.watched_markets: Dict[str, dict] = {}
        
        # 实时赔率缓存
        self._odds_cache: Dict[str, dict] = {}
        self._odds_lock = threading.Lock()
        
        # 回调函数
        self._callbacks: List[Callable] = []
        
        # WebSocket 连接状态
        self._ws_running = False
        self._ws_thread: Optional[threading.Thread] = None
        
        if not self.use_mock:
            self._init_betfair_client()
    
    def _init_betfair_client(self):
        """初始化 Betfair API 客户端"""
        if not self.app_key or not self.session_token:
            logger.warning("Betfair credentials not set. Using mock mode.")
            self.use_mock = True
            return
        
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'X-Application': self.app_key,
                'X-Authentication': self.session_token,
                'Content-Type': 'application/json'
            })
            logger.info("✓ Betfair API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Betfair client: {e}")
            self.use_mock = True
    
    def register_callback(self, callback: Callable):
        """注册赔率变化回调"""
        self._callbacks.append(callback)
    
    def watch_market(self, market_id: str, selection_ids: List[int]):
        """添加监控市场"""
        self.watched_markets[market_id] = {
            "selection_ids": selection_ids,
            "last_odds": {}
        }
        logger.info(f"Watching market: {market_id}")
    
    def start_listening(self):
        """启动赔率监听"""
        if self.use_mock:
            logger.info("Betfair listener running in MOCK mode")
            self._ws_running = True
            self._ws_thread = threading.Thread(
                target=self._mock_odds_generator,
                daemon=True,
                name="BetfairMockThread"
            )
            self._ws_thread.start()
            return
        
        self._ws_running = True
        self._ws_thread = threading.Thread(
            target=self._run_websocket,
            daemon=True,
            name="BetfairWSThread"
        )
        self._ws_thread.start()
        logger.info("✓ Betfair WebSocket listening started")
    
    def stop_listening(self):
        """停止赔率监听"""
        self._ws_running = False
        if self._ws_thread:
            self._ws_thread.join(timeout=5)
        logger.info("Betfair WebSocket listening stopped")
    
    def _run_websocket(self):
        """运行 WebSocket 连接（实际实现需要使用 betfairlightweight 库）"""
        try:
            # 实际生产环境应使用 betfairlightweight 或原生 WebSocket
            # 这里提供骨架实现
            
            import websockets
            import json
            
            ws_url = "wss://stream-api.betfair.com/exchange/v1/stream"
            
            async def connect():
                async with websockets.connect(ws_url) as websocket:
                    # 订阅市场
                    subscription_msg = {
                        "op": "marketSubscription",
                        "marketFilter": {
                            "marketIds": list(self.watched_markets.keys())
                        }
                    }
                    await websocket.send(json.dumps(subscription_msg))
                    
                    # 监听消息
                    async for message in websocket:
                        if not self._ws_running:
                            break
                        
                        data = json.loads(message)
                        self._process_odds_update(data)
            
            # 运行异步循环
            import asyncio
            asyncio.run(connect())
        
        except ImportError:
            logger.warning("websockets not installed. Falling back to HTTP polling.")
            self._http_polling_fallback()
        except Exception as e:
            logger.error(f"Betfair WebSocket error: {e}")
    
    def _http_polling_fallback(self):
        """HTTP 轮询降级方案"""
        while self._ws_running:
            try:
                for market_id in self.watched_markets:
                    odds = self._fetch_market_odds(market_id)
                    if odds:
                        self._process_odds_update(odds)
                
                time.sleep(2)  # 每2秒轮询一次
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)
    
    def _fetch_market_odds(self, market_id: str) -> Optional[Dict[str, Any]]:
        """通过 HTTP API 获取市场赔率"""
        try:
            import requests
            
            url = "https://api.betfair.com/exchange/betting/rest/v1/en/listCurrentOrders/"
            payload = {
                "marketIds": [market_id],
                "orderProjection": "EXECUTABLE"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()  # type: ignore[return-value, no-any-return]
        
        except Exception as e:
            logger.error(f"Failed to fetch odds for {market_id}: {e}")
        
        return None
    
    def _process_odds_update(self, data: dict):
        """处理赔率更新"""
        try:
            # 解析赔率数据并检测异常波动
            market_changes = self._detect_anomalies(data)
            
            if market_changes:
                for change in market_changes:
                    for cb in self._callbacks:
                        try:
                            threading.Thread(
                                target=cb,
                                args=(change,),
                                daemon=True
                            ).start()
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
        
        except Exception as e:
            logger.error(f"Error processing odds update: {e}")
    
    def _detect_anomalies(self, data: dict) -> List[dict[str, Any]]:
        """检测赔率异常波动"""
        anomalies: List[dict[str, Any]] = []
        
        # 简化实现：检测赔率变化超过阈值
        threshold = 0.10  # 10% 变化视为异常
        
        # 实际实现需要更复杂的逻辑
        # 这里仅提供骨架
        
        return anomalies
    
    def get_current_odds(self, market_id: str) -> Optional[dict]:
        """获取当前市场赔率"""
        with self._odds_lock:
            return self._odds_cache.get(market_id)
    
    def _mock_odds_generator(self):
        """Mock 赔率生成器（用于测试）"""
        import random
        
        mock_markets = {
            "EPL_LIVE_1001": {
                "home_win": 2.10,
                "draw": 3.40,
                "away_win": 3.50
            },
            "EPL_LIVE_1002": {
                "home_win": 1.80,
                "draw": 3.60,
                "away_win": 4.20
            }
        }
        
        while self._ws_running:
            for market_id, odds in mock_markets.items():
                # 模拟赔率小幅波动
                changed_odds = {
                    k: round(v * random.uniform(0.95, 1.05), 2)
                    for k, v in odds.items()
                }
                
                with self._odds_lock:
                    self._odds_cache[market_id] = {
                        "timestamp": time.time(),
                        "market_id": market_id,
                        "odds": changed_odds,
                        "source": "betfair_mock"
                    }
                
                # 偶尔触发大幅波动（模拟突发新闻影响）
                if random.random() < 0.1:
                    anomaly = {
                        "market_id": market_id,
                        "type": "sharp_move",
                        "odds_before": odds,
                        "odds_after": changed_odds,
                        "timestamp": time.time()
                    }
                    
                    for cb in self._callbacks:
                        try:
                            threading.Thread(
                                target=cb,
                                args=(anomaly,),
                                daemon=True
                            ).start()
                        except:
                            pass
            
            time.sleep(5)  # 每5秒更新一次
