from functools import lru_cache
from typing import Tuple
from .domain import Transaction, Category
import time

@lru_cache(maxsize=256)
def forecast_expenses(cat_id: str, trans: Tuple[Transaction, ...], period: int) -> int:
    def rec_sum(values):
        if not values:
            return 0
        if len(values) == 1:
            return abs(values[0])
        return abs(values[0]) + rec_sum(values[1:])

    relevant = [t.amount for t in trans if t.cat_id == cat_id and t.amount < 0]
    if not relevant:
        return 0
    total = rec_sum(relevant)
    avg = total // max(1, period)
    return int(avg)

def forecast_expenses_timed(cat_id: str, trans: Tuple[Transaction, ...], period: int):
    t0 = time.perf_counter()
    val = forecast_expenses(cat_id, trans, period)
    t1 = time.perf_counter()
    return val, (t1 - t0) * 1000.0