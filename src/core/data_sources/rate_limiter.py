"""
API限流器 - 智能请求调度
=========================
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    requests: int
    period_seconds: float
    remaining: int
    reset_time: datetime


class TokenBucket:
    """令牌桶算法实现"""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_time(self, tokens: int = 1) -> float:
        with self.lock:
            if self.tokens >= tokens:
                return 0.0
            return (tokens - self.tokens) / self.rate


class RateLimiter:
    """多源限流管理器"""

    def __init__(self):
        self.buckets: dict[str, TokenBucket] = {}
        self.request_history: dict[str, deque] = {}
        self.locks: dict[str, threading.Lock] = {}
        self._init_buckets()

    def _init_buckets(self):
        limits = {
            "api_football": (8.3, 100),
            "football_data": (0.167, 10),
            "odds_api": (0.0004, 1000),
            "the_sports_db": (1000, 10000),
        }

        for name, (rate, capacity) in limits.items():
            self.buckets[name] = TokenBucket(rate, capacity)
            self.request_history[name] = deque(maxlen=1000)
            self.locks[name] = threading.Lock()

    def acquire(self, source: str, timeout: float = 30.0) -> bool:
        bucket = self.buckets.get(source)
        if not bucket:
            return True

        start_time = time.time()
        while time.time() - start_time < timeout:
            if bucket.consume():
                with self.locks[source]:
                    self.request_history[source].append(datetime.now())
                return True
            time.sleep(min(bucket.wait_time(), 1.0))

        logger.warning(f"Rate limit reached for {source}")
        return False

    def get_status(self, source: str) -> dict:
        bucket = self.buckets.get(source)
        if not bucket:
            return {"available": True}

        with self.locks[source]:
            history = self.request_history.get(source, [])
            recent = sum(
                1 for t in history if datetime.now() - t < timedelta(hours=1)
            )

        return {
            "source": source,
            "available": bucket.tokens > 0,
            "remaining_tokens": bucket.tokens,
            "requests_last_hour": recent,
        }

    def get_all_status(self) -> dict:
        return {source: self.get_status(source) for source in self.buckets.keys()}


RATE_LIMITER = RateLimiter()
