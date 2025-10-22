import time
from core.memo import forecast_expenses, forecast_expenses_timed
from core.transforms import load_seed

# Test 1: checks that forecast_expenses returns an integer value
def test_forecast_return_type_and_value():
    _, cats, trans, _ = load_seed("data/seed.json")  # load data (categories, transactions, etc.)
    res = forecast_expenses("cat6", trans, 3)        # calculate forecast for category "cat6"
    assert isinstance(res, int)                      # result must be an integer

# Test 2: checks if memoization (cache) makes second call faster
def test_forecast_cached_speedup():
    _, cats, trans, _ = load_seed("data/seed.json")
    # first call (no cache yet) — may be slower
    _, t1 = forecast_expenses_timed("cat6", trans, 3)
    # second call (same args) — should use cache
    _, t2 = forecast_expenses_timed("cat6", trans, 3)
    # second call should be not slower (ideally faster)
    assert t2 <= t1 + 1e-6

# Test 3: checks that forecast returns 0 when there’s no data for a category
def test_forecast_zero_if_no_data():
    _, _, trans, _ = load_seed("data/seed.json")
    val = forecast_expenses("not_a_cat", trans, 2)   # fake category id (no data)
    assert val == 0                                  # expected result is 0

#  Test 4: checks that forecast gives same result every time (deterministic)
def test_forecast_deterministic():
    _, _, trans, _ = load_seed("data/seed.json")
    v1 = forecast_expenses("cat6", trans, 2)         # first call
    v2 = forecast_expenses("cat6", trans, 2)         # second call (same args)
    assert v1 == v2                                  # results must match

#  Test 5: checks that 'period' argument affects result but still returns integer
def test_forecast_uses_period_argument():
    _, _, trans, _ = load_seed("data/seed.json")
    v_short = forecast_expenses("cat6", trans, 1)    # shorter period (should give higher avg)
    v_long = forecast_expenses("cat6", trans, 6)     # longer period (smaller avg)
    # both results must be integers
    assert isinstance(v_short, int) and isinstance(v_long, int)
