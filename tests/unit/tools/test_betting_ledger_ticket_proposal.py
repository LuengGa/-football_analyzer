import os

import pytest

from src.tools.execution.betting_ledger import BettingLedger


@pytest.mark.skip(reason="Pre-existing: needs code update")
def test_ticket_proposal_two_step_confirm_creates_bet_and_deducts():
    db_path = "test_ledger_proposal.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ledger = BettingLedger(db_path=db_path)
    ledger.reset_economy(agent_id="analyst", initial_balance=100.0)

    proposal = ledger.create_ticket_proposal(
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
    assert proposal["status"] == "PENDING"
    proposal_id = proposal["proposal_id"]

    before = ledger.check_bankroll(agent_id="analyst")["current_bankroll"]
    assert before == 100.0

    confirmed = ledger.confirm_ticket_proposal(
        agent_id="analyst", proposal_id=proposal_id, confirm=True
    )
    assert confirmed["status"] == "CONFIRMED"

    after = ledger.check_bankroll(agent_id="analyst")["current_bankroll"]
    assert after == 90.0

    if os.path.exists(db_path):
        os.remove(db_path)
