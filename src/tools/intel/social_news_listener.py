import time
import os
import threading
from typing import Dict, Any
import requests
import xml.etree.ElementTree as ET
import re
import json

class SocialNewsListener:
    """
    毫秒级情报监听器 (核心逻辑) - ZSA 快轨真实环境版
    通过后台守护线程常驻内存，每隔 30 秒轮询真实的 RSS/Twitter 源。
    当外部通过 MCP 访问时，直接 O(1) 返回内存缓存，实现 0ms 延迟。
    """
    def __init__(self, use_mock: bool = None):
        env_mock = os.getenv("NEWS_LISTENER_MOCK", "false").lower() in ("true", "1", "yes")
        self.use_mock = env_mock if use_mock is None else use_mock
        
        self.rss_feeds = [
            "https://feeds.bbci.co.uk/sport/football/rss.xml",
            "https://www.skysports.com/rss/12040"
        ]
        
        self._cache = {}
        self._cache_lock = threading.Lock()
        
        self.use_local_slm = os.getenv("USE_LOCAL_SLM", "true").lower() in ("true", "1", "yes")
        self.slm_classifier = None
        if self.use_local_slm:
            try:
                from transformers import pipeline
                print("   -> 🧠 [ZSA 快轨] 正在预加载本地轻量级 NLP 模型 (Local SLM)...")
                self.slm_classifier = pipeline(
                    "zero-shot-classification", 
                    model="cross-encoder/nli-distilroberta-base",
                    device=-1
                )
                print("   -> ⚡ [ZSA 快轨] 本地 NLP 模型加载完毕，准备毫秒级推演！")
            except Exception as e:
                print(f"   -> ❌ [ZSA 快轨] 本地模型加载失败，将回退至云端 LLM: {e}")
                self.use_local_slm = False
        
        if not self.use_mock:
            self._polling_thread = threading.Thread(target=self._background_poll, daemon=True)
            self._polling_thread.start()
            print("   -> 🚀 [ZSA 快轨] SocialNewsListener 常驻内存守护线程已启动...")
            
        self._callbacks = []
        self._load_zsa_thresholds()

    def _load_zsa_thresholds(self):
        self.neg_threshold = -0.8
        self.pos_threshold = 0.5
        try:
            hp_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "hyperparams.json")
            if os.path.exists(hp_path):
                with open(hp_path, "r", encoding="utf-8") as f:
                    params = json.load(f)
                    zsa_t = params.get("zsa_thresholds", {})
                    if "negative_impact_threshold" in zsa_t:
                        self.neg_threshold = float(zsa_t["negative_impact_threshold"])
                    if "positive_impact_threshold" in zsa_t:
                        self.pos_threshold = float(zsa_t["positive_impact_threshold"])
        except Exception:
            pass

    def register_callback(self, callback_func):
        self._callbacks.append(callback_func)

    def _fire_callbacks(self, team: str, news: str, impact: float):
        for cb in self._callbacks:
            try:
                threading.Thread(target=cb, args=(team, news, impact), daemon=True).start()
            except Exception as e:
                print(f"   -> ⚠️ [ZSA 快轨] 回调执行异常: {e}")

    def _background_poll(self):
        while True:
            try:
                all_news = []
                for url in self.rss_feeds:
                    resp = requests.get(url, timeout=5)
                    if resp.status_code == 200:
                        root = ET.fromstring(resp.content)
                        for item in root.findall('./channel/item'):
                            title = item.find('title').text or ""
                            desc = item.find('description').text or ""
                            all_news.append((title, desc))
                
                with self._cache_lock:
                    watched_teams = list(self._cache.keys())
                
                for team in watched_teams:
                    team_news = []
                    for title, desc in all_news:
                        if team.lower() in title.lower() or team.lower() in desc.lower():
                            team_news.append(f"{title}: {desc}")
                    
                    if team_news:
                        combined = " | ".join(team_news[:3])
                        current_cached = self._cache.get(team, {}).get("news", "")
                        if combined != current_cached:
                            xg_impact = self._analyze_xg_impact_with_llm(team, combined)
                            
                            if xg_impact <= self.neg_threshold or xg_impact >= self.pos_threshold:
                                self._fire_callbacks(team, combined, xg_impact)
                                
                            with self._cache_lock:
                                self._cache[team] = {
                                    "timestamp": time.time(),
                                    "team": team,
                                    "news": combined,
                                    "xg_impact": xg_impact,
                                    "source": "rss_aggregator_cache",
                                    "latency_ms": 0
                                }
            except Exception:
                pass
                
            time.sleep(30)

    def fetch_latest_news(self, team_name: str) -> Dict[str, Any]:
        if self.use_mock:
            return self._mock_news(team_name)

        start_t = time.perf_counter()
        
        with self._cache_lock:
            if team_name not in self._cache:
                self._cache[team_name] = {
                    "timestamp": time.time(),
                    "team": team_name,
                    "news": "系统刚开始监听该球队，等待下一次数据面刷新...",
                    "xg_impact": 0.0,
                    "source": "rss_aggregator_cache_init",
                    "latency_ms": 0
                }
                threading.Thread(target=self._force_sync_fetch, args=(team_name,), daemon=True).start()
            
            result = dict(self._cache[team_name])
            
        end_t = time.perf_counter()
        result["latency_ms"] = round((end_t - start_t) * 1000, 2)
        return result

    def _force_sync_fetch(self, team_name: str):
        print(f"   -> 📡 [ZSA 快轨] 首次扫描 {team_name} 的情报入缓存...")
        news_items = []
        try:
            for url in self.rss_feeds:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    for item in root.findall('./channel/item'):
                        title = item.find('title').text or ""
                        desc = item.find('description').text or ""
                        if team_name.lower() in title.lower() or team_name.lower() in desc.lower():
                            news_items.append(f"{title}: {desc}")
        except Exception:
            pass

        if news_items:
            combined = " | ".join(news_items[:3])
            xg_impact = self._analyze_xg_impact_with_llm(team_name, combined)
            
            if xg_impact <= self.neg_threshold or xg_impact >= self.pos_threshold:
                self._fire_callbacks(team_name, combined, xg_impact)
                
            with self._cache_lock:
                self._cache[team_name] = {
                    "timestamp": time.time(),
                    "team": team_name,
                    "news": combined,
                    "xg_impact": xg_impact,
                    "source": "rss_aggregator_cache",
                    "latency_ms": 0
                }

    def _analyze_xg_impact_with_llm(self, team_name: str, news_text: str) -> float:
        if getattr(self, 'use_local_slm', False) and getattr(self, 'slm_classifier', None):
            return self._analyze_with_local_slm(team_name, news_text)
        else:
            return self._analyze_with_cloud_llm(team_name, news_text)

    def _analyze_with_local_slm(self, team_name: str, news_text: str) -> float:
        if not self.slm_classifier:
            return 0.0
            
        try:
            candidate_labels = [
                "player injury", 
                "player suspension", 
                "red card", 
                "player return from injury", 
                "team morale boost", 
                "neutral news"
            ]
            
            result = self.slm_classifier(
                news_text, 
                candidate_labels,
                hypothesis_template="This football news is about {}."
            )
            
            top_label = result['labels'][0]
            confidence = result['scores'][0]
            
            impact = 0.0
            negative_labels = ["player injury", "player suspension", "red card"]
            positive_labels = ["player return from injury", "team morale boost"]
            
            if top_label in negative_labels:
                if confidence > 0.55:
                    impact = -0.8
                elif confidence >= 0.40:
                    if any(kw in news_text.lower() for kw in ["injur", "miss", "out", "red card", "suspend", "缺阵", "伤", "红牌"]):
                        impact = -0.8
            elif top_label in positive_labels:
                if confidence > 0.55:
                    impact = 0.3
                elif confidence >= 0.40:
                    if any(kw in news_text.lower() for kw in ["return", "back", "boost", "复出", "回归", "振奋"]):
                        impact = 0.3
            
            return impact
            
        except Exception:
            return 0.0

    def _analyze_with_cloud_llm(self, team_name: str, news_text: str) -> float:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
        model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")

        if not api_key:
            return 0.0

        try:
            import openai
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = openai.OpenAI(**client_kwargs)

            prompt = f"""
你是专业的足球量化分析师。请评估以下关于 {team_name} 的新闻对他们本场比赛的预期进球数(xG)的影响。
新闻：{news_text}

规则：
- 如果是核心前锋受伤/红牌，xg_impact 在 -0.5 到 -1.0 之间
- 如果是防守核心受伤，不影响己方 xG，可能影响对方 xG
- 如果是核心复出或士气大振，xg_impact 在 +0.2 到 +0.5 之间
- 如果是普通新闻或无关紧要，输出 0.0

请只输出一个浮点数，不要有任何其他字符。例如: -0.5
"""
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            impact_str = response.choices[0].message.content.strip()
            match = re.search(r'-?\d+\.\d+', impact_str)
            if match:
                return float(match.group())
            return float(impact_str)
        except Exception:
            return 0.0

    def _mock_news(self, team_name: str) -> Dict[str, Any]:
        import random
        mock_news_pool = [
            {"text": f"【突发】{team_name} 核心前锋在赛前热身时大腿拉伤，已退出大名单！", "xg_impact": -0.8},
            {"text": f"【常规】{team_name} 主教练出席赛前发布会，表示全队士气高昂。", "xg_impact": 0.0}
        ]
        news = random.choice(mock_news_pool)
        return {
            "timestamp": time.time(),
            "team": team_name,
            "news": news["text"],
            "xg_impact": news["xg_impact"],
            "source": "twitter_insider_webhook",
            "latency_ms": random.randint(15, 80)
        }

    def inject_mock_news(self, team_name: str, news_text: str, impact: float):
        with self._cache_lock:
            self._cache[team_name] = {
                "timestamp": time.time(),
                "team": team_name,
                "news": news_text,
                "xg_impact": impact,
                "source": "manual_inject",
                "latency_ms": 0
            }
        print(f"   -> 💉 [ZSA 快轨] 手动注入情报: {news_text} (Impact: {impact})")
        if impact <= self.neg_threshold or impact >= self.pos_threshold:
            self._fire_callbacks(team_name, news_text, impact)
