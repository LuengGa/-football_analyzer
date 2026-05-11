"""
AFA Plugin System — 插件架构
=============================

基于OpenClaw风格的插件系统：
- 插件生命周期管理（load/unload/enable/disable）
- 插件依赖解析
- 热插拔支持
- 插件API标准接口

插件类型：
- data: 数据源插件
- analysis: 分析插件
- execution: 执行插件
- intel: 情报插件
"""

from typing import Any, Optional, List, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum
import importlib
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginType(Enum):
    DATA = "data"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    INTEL = "intel"
    CUSTOM = "custom"


class PluginState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginMetadata:
    id: str
    name: str
    version: str
    plugin_type: PluginType
    description: str
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    hooks: List[str] = field(default_factory=list)


@dataclass
class Plugin:
    metadata: PluginMetadata
    module: Any
    state: PluginState = PluginState.UNLOADED
    config: Dict[str, Any] = field(default_factory=dict)
    instance: Any = None
    loaded_at: Optional[datetime] = None

    def enable(self) -> bool:
        if self.state != PluginState.LOADED:
            return False
        self.state = PluginState.ENABLED
        return True

    def disable(self) -> bool:
        if self.state != PluginState.ENABLED:
            return False
        self.state = PluginState.DISABLED
        return True


class PluginInterface:
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id

    def on_load(self, config: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def on_enable(self) -> bool:
        raise NotImplementedError

    def on_disable(self) -> bool:
        raise NotImplementedError

    def on_unload(self) -> None:
        raise NotImplementedError

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class PluginHook:
    def __init__(self, name: str, callback: Callable, priority: int = 0):
        self.name = name
        self.callback = callback
        self.priority = priority


class PluginRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._plugins: Dict[str, Plugin] = {}
        self._hooks: Dict[str, List[PluginHook]] = {}
        self._hooks_by_plugin: Dict[str, List[str]] = {}
        self._initialized = True

    def register_plugin(self, plugin: Plugin) -> bool:
        if plugin.metadata.id in self._plugins:
            logger.warning(f"Plugin {plugin.metadata.id} already registered")
            return False
        self._plugins[plugin.metadata.id] = plugin
        logger.info(f"Plugin {plugin.metadata.id} registered")
        return True

    def unregister_plugin(self, plugin_id: str) -> bool:
        if plugin_id not in self._plugins:
            return False
        plugin = self._plugins[plugin_id]
        if plugin.state in (PluginState.ENABLED, PluginState.LOADING):
            self.disable_plugin(plugin_id)
        del self._plugins[plugin_id]
        logger.info(f"Plugin {plugin_id} unregistered")
        return True

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        return self._plugins.get(plugin_id)

    def list_plugins(self, plugin_type: Optional[PluginType] = None,
                    state: Optional[PluginState] = None) -> List[Plugin]:
        results = list(self._plugins.values())
        if plugin_type:
            results = [p for p in results if p.metadata.plugin_type == plugin_type]
        if state:
            results = [p for p in results if p.state == state]
        return results

    def load_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            logger.error(f"Plugin {plugin_id} not found")
            return False

        if plugin.state not in (PluginState.UNLOADED, PluginState.DISABLED):
            logger.warning(f"Plugin {plugin_id} already loaded (state: {plugin.state})")
            return False

        plugin.state = PluginState.LOADING
        try:
            if hasattr(plugin.module, 'on_load'):
                if config:
                    plugin.config.update(config)
                result = plugin.module.on_load(plugin.config)
                if not result:
                    plugin.state = PluginState.ERROR
                    return False

            plugin.instance = plugin.module
            plugin.state = PluginState.LOADED
            plugin.loaded_at = datetime.now()
            logger.info(f"Plugin {plugin_id} loaded successfully")
            self._execute_hook(f"after_load_{plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            plugin.state = PluginState.ERROR
            return False

    def enable_plugin(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return False

        if plugin.state == PluginState.UNLOADED:
            if not self.load_plugin(plugin_id):
                return False

        if plugin.state != PluginState.LOADED:
            return False

        try:
            if hasattr(plugin.instance, 'on_enable'):
                if not plugin.instance.on_enable():
                    return False
            plugin.state = PluginState.ENABLED
            logger.info(f"Plugin {plugin_id} enabled")
            self._execute_hook(f"after_enable_{plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            plugin.state = PluginState.ERROR
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin or plugin.state != PluginState.ENABLED:
            return False

        try:
            if hasattr(plugin.instance, 'on_disable'):
                plugin.instance.on_disable()
            plugin.state = PluginState.DISABLED
            logger.info(f"Plugin {plugin_id} disabled")
            self._execute_hook(f"after_disable_{plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return False

        if plugin.state == PluginState.ENABLED:
            self.disable_plugin(plugin_id)

        if plugin.state not in (PluginState.LOADED, PluginState.DISABLED, PluginState.ERROR):
            return False

        try:
            if hasattr(plugin.instance, 'on_unload'):
                plugin.instance.on_unload()
            plugin.state = PluginState.UNLOADED
            plugin.instance = None
            logger.info(f"Plugin {plugin_id} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False

    def register_hook(self, plugin_id: str, name: str, callback: Callable, priority: int = 0) -> None:
        hook = PluginHook(name, callback, priority)
        if name not in self._hooks:
            self._hooks[name] = []
        self._hooks[name].append(hook)
        self._hooks[name].sort(key=lambda h: h.priority, reverse=True)

        if plugin_id not in self._hooks_by_plugin:
            self._hooks_by_plugin[plugin_id] = []
        self._hooks_by_plugin[plugin_id].append(name)

    def _execute_hook(self, name: str, *args, **kwargs) -> List[Any]:
        results = []
        for hook in self._hooks.get(name, []):
            try:
                result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {name} failed: {e}")
        return results

    def execute_hook(self, name: str, *args, **kwargs) -> List[Any]:
        return self._execute_hook(name, *args, **kwargs)

    def load_plugins_from_directory(self, plugin_dir: Path) -> int:
        loaded = 0
        if not plugin_dir.exists():
            return 0

        for plugin_file in plugin_dir.glob("*.json"):
            try:
                with open(plugin_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                plugin = self.create_plugin_from_manifest(meta)
                if plugin:
                    self.register_plugin(plugin)
                    loaded += 1
            except Exception as e:
                logger.error(f"Failed to load plugin manifest {plugin_file}: {e}")

        return loaded

    def create_plugin_from_manifest(self, manifest: Dict[str, Any]) -> Optional[Plugin]:
        try:
            metadata = PluginMetadata(
                id=manifest["id"],
                name=manifest["name"],
                version=manifest["version"],
                plugin_type=PluginType(manifest.get("type", "custom")),
                description=manifest.get("description", ""),
                author=manifest.get("author", ""),
                dependencies=manifest.get("dependencies", []),
                config_schema=manifest.get("config_schema", {}),
                hooks=manifest.get("hooks", []),
            )
            module = None
            if "module" in manifest:
                try:
                    module = importlib.import_module(manifest["module"])
                except ImportError as e:
                    logger.warning(f"Plugin module {manifest['module']} not found: {e}")
                    return None

            return Plugin(metadata=metadata, module=module or type("Module", (), {})())
        except Exception as e:
            logger.error(f"Invalid plugin manifest: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total": len(self._plugins),
            "by_state": {
                state.value: len([p for p in self._plugins.values() if p.state == state])
                for state in PluginState
            },
            "by_type": {
                ptype.value: len([p for p in self._plugins.values() if p.metadata.plugin_type == ptype])
                for ptype in PluginType
            },
        }


PLUGIN_REGISTRY = PluginRegistry()

__all__ = [
    "PluginType",
    "PluginState",
    "PluginMetadata",
    "Plugin",
    "PluginInterface",
    "PluginHook",
    "PluginRegistry",
    "PLUGIN_REGISTRY",
]
