"""
AFA Task Queue — 后台任务队列
=============================

基于持久化队列的后台任务系统：
- 任务持久化（SQLite）
- 优先级队列
- 任务状态跟踪
- 定时任务
- 重试机制
"""

import sqlite3
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import queue

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    id: str
    name: str
    func_name: str
    args: tuple
    kwargs: dict
    priority: int
    status: str
    created_at: str
    scheduled_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[str]
    error: Optional[str]
    retry_count: int
    max_retries: int
    metadata: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: tuple) -> "Task":
        return cls(
            id=row[0], name=row[1], func_name=row[2],
            args=json.loads(row[3]) if row[3] else (),
            kwargs=json.loads(row[4]) if row[4] else {},
            priority=row[5], status=row[6], created_at=row[7],
            scheduled_at=row[8], started_at=row[9], completed_at=row[10],
            result=row[11], error=row[12], retry_count=row[13],
            max_retries=row[14], metadata=row[15] or "{}"
        )


class TaskQueue:
    _instance: Optional["TaskQueue"] = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return

        if db_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            data_dir = project_root / "data" / "tasks"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "task_queue.db")

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._registry: Dict[str, Callable] = {}
        self._init_db()
        self._initialized = True

    def _init_db(self) -> None:
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                func_name TEXT NOT NULL,
                args TEXT,
                kwargs TEXT,
                priority INTEGER DEFAULT 1,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                scheduled_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                metadata TEXT DEFAULT '{}'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled ON tasks(scheduled_at)")
        self._conn.commit()

    def register(self, func_name: str, func: Callable) -> None:
        self._registry[func_name] = func

    def enqueue(self, func_name: str, *args, name: str = "", priority: int = 1,
                scheduled_at: Optional[datetime] = None, max_retries: int = 3,
                **kwargs) -> str:
        if func_name not in self._registry:
            raise ValueError(f"Function {func_name} not registered")

        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        task = Task(
            id=task_id,
            name=name or func_name,
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            priority=priority,
            status=TaskStatus.PENDING.value,
            created_at=now,
            scheduled_at=scheduled_at.isoformat() if scheduled_at else None,
            started_at=None,
            completed_at=None,
            result=None,
            error=None,
            retry_count=0,
            max_retries=max_retries,
            metadata="{}"
        )

        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("""
            INSERT INTO tasks (id, name, func_name, args, kwargs, priority, status, created_at, scheduled_at, retry_count, max_retries, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task.id, task.name, task.func_name, json.dumps(task.args), json.dumps(task.kwargs),
              task.priority, task.status, task.created_at, task.scheduled_at,
              task.retry_count, task.max_retries, task.metadata))
        self._conn.commit()  # type: ignore[union-attr]

        self._queue.put((priority, task_id))
        logger.info(f"Task {task_id} enqueued: {task.name}")
        return task_id

    def dequeue(self) -> Optional[Task]:
        try:
            priority, task_id = self._queue.get_nowait()
        except queue.Empty:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("""
                SELECT * FROM tasks
                WHERE status = 'pending'
                AND (scheduled_at IS NULL OR scheduled_at <= ?)
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """, (datetime.now().isoformat(),))
            row = cursor.fetchone()
            if not row:
                return None
            task = Task.from_row(row)
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (TaskStatus.RUNNING.value, task.id))
            self._conn.commit()  # type: ignore[union-attr]
            return task

        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        task = Task.from_row(row)
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (TaskStatus.RUNNING.value, task.id))
        self._conn.commit()  # type: ignore[union-attr]
        return task

    def complete(self, task_id: str, result: Any) -> None:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("""
            UPDATE tasks SET status = ?, completed_at = ?, result = ?
            WHERE id = ?
        """, (TaskStatus.COMPLETED.value, datetime.now().isoformat(), json.dumps(result), task_id))
        self._conn.commit()
        logger.info(f"Task {task_id} completed")

    def fail(self, task_id: str, error: str) -> None:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("SELECT retry_count, max_retries FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row and row[0] < row[1]:
            cursor.execute("""
                UPDATE tasks SET status = ?, error = ?, retry_count = retry_count + 1
                WHERE id = ?
            """, (TaskStatus.RETRY.value, error, task_id))
            self._conn.commit()
            logger.info(f"Task {task_id} scheduled for retry ({row[0]+1}/{row[1]})")
        else:
            cursor.execute("""
                UPDATE tasks SET status = ?, error = ?, completed_at = ?
                WHERE id = ?
            """, (TaskStatus.FAILED.value, error, datetime.now().isoformat(), task_id))
            self._conn.commit()
            logger.error(f"Task {task_id} failed: {error}")

    def cancel(self, task_id: str) -> bool:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ? AND status = 'pending'", (TaskStatus.CANCELLED.value, task_id))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_task(self, task_id: str) -> Optional[Task]:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return Task.from_row(row) if row else None

    def list_tasks(self, status: Optional[str] = None, limit: int = 50) -> List[Task]:
        cursor = self._conn.cursor()
        if status:
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?", (status, limit))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        return [Task.from_row(row) for row in cursor.fetchall()]

    def start_worker(self) -> None:
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info("Task queue worker started")

    def stop_worker(self) -> None:
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("Task queue worker stopped")

    def _worker_loop(self) -> None:
        while self._running:
            task = self.dequeue()
            if not task:
                time.sleep(1)
                continue

            try:
                func = self._registry.get(task.func_name)
                if func:
                    result = func(*task.args, **task.kwargs)
                    self.complete(task.id, result)
                else:
                    self.fail(task.id, f"Function {task.func_name} not found")
            except Exception as e:
                self.fail(task.id, str(e))

    def get_stats(self) -> Dict[str, Any]:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        by_status = dict(cursor.fetchall())
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]
        return {
            "total": total,
            "by_status": by_status,
            "queue_size": self._queue.qsize(),
            "running": by_status.get("running", 0),
            "pending": by_status.get("pending", 0),
            "completed": by_status.get("completed", 0),
            "failed": by_status.get("failed", 0),
        }

    def close(self) -> None:
        self.stop_worker()
        if self._conn:
            self._conn.close()


TASK_QUEUE = TaskQueue()

__all__ = ["TaskStatus", "TaskPriority", "Task", "TaskQueue", "TASK_QUEUE"]
