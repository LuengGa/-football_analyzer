"""EventBus for decoupled communication between modules"""
from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class EventBus:
    """Simple in-memory event bus for pub/sub between modules."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable) -> None:
        self._subscribers.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._subscribers:
            self._subscribers[event] = [cb for cb in self._subscribers[event] if cb != callback]

    async def publish(self, event: str, data: Any = None) -> None:
        for cb in self._subscribers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                logger.error(f"EventBus callback error for {event}: {e}")

    def has_subscribers(self, event: str) -> bool:
        return bool(self._subscribers.get(event))
