"""
AFA v9 Configuration Manager — 统一配置管理
==========================================

支持YAML/JSON格式配置加载，自动合并环境变量覆盖
"""

import os
import json
import yaml
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfigSection:
    name: str
    data: Dict[str, Any]
    source: str = ""


class ConfigManager:
    _instance = None

    def __new__(cls, config_dir: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized: bool = False  # type: ignore[has-type]
        return cls._instance

    def __init__(self, config_dir: Optional[str] = None):
        if self._initialized:
            return

        if config_dir is None:
            self.config_dir = self._find_config_dir()
        else:
            self.config_dir = Path(config_dir)

        self._config: Dict[str, Any] = {}
        self._sections: Dict[str, ConfigSection] = {}
        self._load_all()
        self._initialized = True  # type: ignore[has-type]

    def _find_config_dir(self) -> Path:
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            candidate = parent / "configs" / "afa_v9"
            if candidate.exists() and candidate.is_dir():
                return candidate
        for parent in [current] + list(current.parents):
            candidate = parent / "configs"
            if candidate.exists() and candidate.is_dir():
                afa_candidate = candidate / "afa_v9"
                if afa_candidate.exists():
                    return afa_candidate
                return candidate
        return current.parent.parent.parent / "configs" / "afa_v9"

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML {file_path}: {e}")
            return {}

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON {file_path}: {e}")
            return {}

    def _load_all(self) -> None:
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            return

        for config_file in self.config_dir.glob("*.yaml"):
            name = config_file.stem
            data = self._load_yaml(config_file)
            self._config[name] = data
            self._sections[name] = ConfigSection(name=name, data=data, source=str(config_file))

        for config_file in self.config_dir.glob("*.json"):
            name = config_file.stem
            if name not in self._config:
                data = self._load_json(config_file)
                self._config[name] = data
                self._sections[name] = ConfigSection(name=name, data=data, source=str(config_file))

        logger.info(f"Loaded {len(self._sections)} config sections from {self.config_dir}")

    def _get_nested(self, data: Dict, keys: list) -> Any:
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)  # type: ignore[assignment]
            else:
                return None
        return data  # type: ignore[return-value]

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split(".")
        value = None

        if parts[0] in self._config:
            value = self._get_nested(self._config[parts[0]], parts[1:])
        else:
            for section in self._config.values():
                value = self._get_nested(section, parts)
                if value is not None:
                    break

        if value is None:
            value = default

        return self._resolve_env_override(key, value, default)

    def _resolve_env_override(self, key: str, value: Any, default: Any) -> Any:
        env_key = f"AFA_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            try:
                if value is None:
                    return json.loads(env_value)
                if isinstance(value, bool):
                    return env_value.lower() in ("true", "1", "yes")
                if isinstance(value, int):
                    return int(env_value)
                if isinstance(value, float):
                    return float(env_value)
                return env_value
            except (json.JSONDecodeError, ValueError):
                return env_value
        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        return self._config.get(section, {})

    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

    def reload(self) -> None:
        self._config.clear()
        self._sections.clear()
        self.config_dir = self._find_config_dir()
        self._load_all()

    def set(self, key: str, value: Any) -> None:
        parts = key.split(".")
        if parts[0] in self._config:
            config = self._config[parts[0]]
            for part in parts[1:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            self._config[parts[0]] = {}
            config = self._config[parts[0]]
            for part in parts[1:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        return self.get_all()


SYSTEM_CONFIG = ConfigManager()
AGENTS_CONFIG = SYSTEM_CONFIG.get_section("agents")
SKILLS_CONFIG = SYSTEM_CONFIG.get_section("skills")


def get_config(key: str, default: Any = None) -> Any:
    return SYSTEM_CONFIG.get(key, default)


def get_system_config() -> Dict[str, Any]:
    return SYSTEM_CONFIG.get_section("system")


def get_agents_config() -> Dict[str, Any]:
    return SYSTEM_CONFIG.get_section("agents")


def get_skills_config() -> Dict[str, Any]:
    return SYSTEM_CONFIG.get_section("skills")


__all__ = [
    "ConfigManager",
    "SYSTEM_CONFIG",
    "AGENTS_CONFIG",
    "SKILLS_CONFIG",
    "get_config",
    "get_system_config",
    "get_agents_config",
    "get_skills_config",
]
