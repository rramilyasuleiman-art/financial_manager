import pytest
from core.transforms import load_seed, add_transaction, update_budget, account_balance
from core.domain import Transaction, Budget
from pathlib import Path

DATA = Path("data/seed.json")

def test_load_seed_counts():
    accs, cats, trans, buds = load_seed(str(DATA))
    assert len(accs) >= 3
    assert len(cats) >= 10
    assert len(trans) >= 100
    assert len(buds) >= 3

def test_add_transaction_returns_new_tuple():
    _, _, trans, _ = load_seed(str(DATA))
    t = Transaction("tx_test", "acc1", "cat6", -111, "2025-05-01T00:00:00", "test", "test note")

    new = add_transaction(trans, t)
    assert isinstance(new, tuple)
    assert len(new) == len(trans) + 1
    assert new[-1].id == "tx_test"

def test_update_budget_returns_new_collection():
    _, _, _, buds = load_seed(str(DATA))
    orig = buds
    updated = update_budget(buds, buds[0].id, 99999)
    assert isinstance(updated, tuple)
    assert updated[0].limit == 99999
    assert orig != updated

def test_account_balance_reduce_positive_and_negative():
    _, _, trans, _ = load_seed(str(DATA))
    # pick acc3 which has several incomes
    bal = account_balance(trans, "acc3")
    assert isinstance(bal, int)

def test_immutability_dataclass_frozen():
    _, _, _, _ = load_seed(str(DATA))
    b = Budget("bx", "cat6", 100, "month")
    with pytest.raises(Exception):
        b.limit = 200
