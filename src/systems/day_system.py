"""Pengelolaan pergantian hari dan batas penjualan harian."""


class DaySystem:
    @staticmethod
    def can_sell(player) -> bool:
        return player.daily_sales < player.daily_sell_limit

    @staticmethod
    def register_sale(player) -> None:
        if not DaySystem.can_sell(player):
            raise ValueError("Batas penjualan hari ini sudah tercapai.")
        player.daily_sales += 1
        player.total_items_sold += 1

    @staticmethod
    def end_day(player) -> None:
        player.day += 1
        player.daily_sales = 0
