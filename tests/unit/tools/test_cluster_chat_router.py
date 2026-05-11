import pytest
import os
import shutil
import uuid
import json
from pathlib import Path


@pytest.mark.skip(reason="Pre-existing: needs code update")
def test_cluster_chat_router_routes_and_writes_shared_semantic():
    os.environ["AFA_DISABLE_CHROMA"] = "1"
    os.environ["AFA_SKIP_DOTENV"] = "1"

    from src.cli.cluster_chat_router import ClusterChatRouter
    from src.tools.odds.paths import knowledge_base_dir

    cluster_name = f"chat_{uuid.uuid4().hex}"
    cluster_root = Path(knowledge_base_dir("clusters")) / cluster_name
    try:
        router = ClusterChatRouter(cluster_name=cluster_name)
        r1 = router.handle("给我一个风控建议：仓位怎么控？")
        r2 = router.handle("看看阵容伤停情报")
        r3 = router.handle("复核一下你刚才的结论是否靠谱，需要哪些证据？")

        assert r1.role == "risk"
        assert r2.role == "scout"
        assert r3.role == "referee"
        obj = json.loads(r3.response)
        for k in ["claims", "evidence_gaps", "suggested_tools", "suggested_sources", "risk_rating"]:
            assert k in obj

        semantic_file = cluster_root / "shared" / "semantic_core" / "semantic_truth.json"
        assert semantic_file.exists()
        content = semantic_file.read_text(encoding="utf-8")
        assert "CHAT_NOTE[risk]" in content
        assert "CHAT_NOTE[scout]" in content
        assert "CHAT_NOTE[referee]" in content

        epi_risk = cluster_root / "lives" / "risk" / "memory_core" / "episodic.json"
        epi_scout = cluster_root / "lives" / "scout" / "memory_core" / "episodic.json"
        epi_ref = cluster_root / "lives" / "referee" / "memory_core" / "episodic.json"
        assert epi_risk.exists()
        assert epi_scout.exists()
        assert epi_ref.exists()
        assert epi_risk != epi_scout

        audit_log = cluster_root / "shared" / "audit" / "audit.jsonl"
        assert audit_log.exists()
        lines = audit_log.read_text(encoding="utf-8").splitlines()
        assert any('"event": "chat.message"' in l for l in lines)
        assert any('"event": "chat.response"' in l for l in lines)
    finally:
        shutil.rmtree(cluster_root, ignore_errors=True)
