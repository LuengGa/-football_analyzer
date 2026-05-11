import asyncio

import pytest

from src.tools.odds.multisource_fetcher import MultiSourceFetcher


@pytest.mark.skip(reason="Pre-existing: needs MultiSourceFetcher mock/fixture")
async def test_fallback_never_crash():
    f = MultiSourceFetcher()
    res = await f.fetch_odds(home_team="皇家马德里", away_team="曼城")
    assert "ok" in res and "meta" in res
    if res["ok"]:
        assert "confidence" in res["meta"]
    else:
        assert res["error"]["code"] in [
            "CAPTCHA_REQUIRED",
            "NOT_FOUND",
            "FETCH_FAILED",
            "BAD_INPUT",
        ]


if __name__ == "__main__":
    asyncio.run(test_fallback_never_crash())
    print("test_fallback_never_crash PASSED")
