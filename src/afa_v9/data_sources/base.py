"""
AFA v9.0 数据源基类

统一的数据获取接口
"""

from abc import ABC
from typing import Any, Dict, Optional, Union
from datetime import datetime
import time
import requests  # type: ignore[import-untyped]


class BaseDataSource(ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_request_time: float = 0.0
        self.request_count = 0
        self.rate_limit_delay = 1.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        self._rate_limit()
        self.request_count += 1

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "request_count": self.request_count,
            "last_request": datetime.fromtimestamp(self.last_request_time).isoformat()
                if self.last_request_time > 0 else None,
        }
