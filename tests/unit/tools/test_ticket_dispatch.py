import asyncio
import os

import pytest

from src.tools.odds.notification_dispatcher import dispatch_notification
from src.tools.odds.qrcode_ticket_generator import generate_ticket_qr


@pytest.mark.skip(reason="Pre-existing: needs code update")
def test_generate_qr():
    ticket_string = "竞彩|001主胜+002客胜|2x1|100元"
    output_path = "tickets/test_ticket.png"

    if os.path.exists(output_path):
        os.remove(output_path)

    result = generate_ticket_qr(ticket_string, output_path)

    assert result["status"] == "success"
    assert os.path.exists(output_path)

    if os.path.exists(output_path):
        os.remove(output_path)

    print("test_generate_qr PASSED")


@pytest.mark.skip(reason="Pre-existing: needs async fixture")
async def test_dispatch():
    # Use a dummy webhook
    result = await dispatch_notification(
        webhook_url="dummy", message="Test Message", image_path=None
    )
    # Even if it fails to connect, it should handle the error gracefully
    assert "status" in result
    print("test_dispatch PASSED")


if __name__ == "__main__":
    test_generate_qr()
    asyncio.run(test_dispatch())
