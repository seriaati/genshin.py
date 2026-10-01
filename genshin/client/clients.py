"""A simple HTTP client for API endpoints."""

from .components import (
    auth,
    calculator,
    card_plaza,
    chronicle,
    daily,
    diary,
    gacha,
    hoyolab,
    hsr_lineup,
    hsr_warp_records,
    lineup,
    teapot,
    transaction,
    wiki,
)

__all__ = ["Client"]


class Client(
    chronicle.BattleChronicleClient,
    hoyolab.HoyolabClient,
    daily.DailyRewardClient,
    calculator.CalculatorClient,
    diary.DiaryClient,
    lineup.LineupClient,
    card_plaza.CardPlazaClient,
    teapot.TeapotClient,
    wiki.WikiClient,
    gacha.WishClient,
    transaction.TransactionClient,
    auth.AuthClient,
    hsr_lineup.HSRLineupClient,
    hsr_warp_records.HSRWarpRecordsClient,
):
    """A simple HTTP client for API endpoints."""
