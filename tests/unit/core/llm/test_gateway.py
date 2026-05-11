import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.llm.gateway import LLMGateway, ProviderType, LLM_GATEWAY


def test_gateway_initialization():
    gateway = LLMGateway()
    assert gateway is not None
    assert isinstance(gateway.providers, dict)


def test_route_task_types():
    gateway = LLMGateway()
    provider = gateway.route("analysis")
    assert provider in ProviderType


def test_route_reasoning():
    gateway = LLMGateway()
    provider = gateway.route("reasoning")
    assert provider in ProviderType


def test_get_available_providers():
    gateway = LLMGateway()
    providers = gateway.get_available_providers()
    assert isinstance(providers, list)


def test_singleton_instance():
    assert LLM_GATEWAY is not None
    assert isinstance(LLM_GATEWAY, LLMGateway)
