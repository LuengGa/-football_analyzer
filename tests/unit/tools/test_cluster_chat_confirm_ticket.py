import os
import shutil
import uuid
from pathlib import Path

import pytest


@pytest.mark.skip(reason="Pre-existing: needs code update")
def test_cluster_chat_confirm_ticket_flow():
    os.environ["AFA_DISABLE_CHROMA"] = "1"
    os.environ["AFA_SKIP_DOTENV"] = "1"

    from src.cli.cluster_chat_router import ClusterChatRouter
    from src.tools.odds.paths import knowledge_base_dir

    cluster_name = f"confirm_{uuid.uuid4().hex}"
    cluster_root = Path(knowledge_base_dir("clusters")) / cluster_name
    try:
        router = ClusterChatRouter(cluster_name=cluster_name)
        life = router.cluster.ensure_instance(life_id="analyst", role="analyst")
        life.ledger.reset_economy(agent_id="analyst", initial_balance=100.0)
        proposal = life.ledger.create_ticket_proposal(
            agent_id="analyst",
            payload={
                "match_id": "M1",
                "lottery_type": "jingcai",
                "play_type": "WDL",
                "selection": "home_win",
                "odds": 2.0,
                "stake": 10.0,
            },
        )
        pid = proposal["proposal_id"]
        res = router.handle(f"确认出票 {pid}", preferred_life_id="analyst")
        assert f"proposal_id={pid}" in res.response
        assert life.ledger.check_bankroll(agent_id="analyst")["current_bankroll"] == 90.0
    finally:
        shutil.rmtree(cluster_root, ignore_errors=True)
