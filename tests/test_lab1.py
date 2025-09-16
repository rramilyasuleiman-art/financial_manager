from pathlib import Path
from core.domain import Transaction
from core.transforms import add_transaction, update_budget, account_balance, load_seed

ROOT = Path(__file__).parents[1]
SEED = ROOT / "data" / "seed.json"

def test_load_seed_has_collections():
    trans, buds = load_seed(SEED)
    assert isinstance(trans, tuple)
    assert isinstance(buds, tuple)
    assert len(trans) >= 5
    assert len(buds) >= 3

def test_add_transaction_returns_new_tuple():
    trans, _ = load_seed(SEED)
    t = Transaction(id="tx_test", account_id="a1", cat_id="c_other", amount=-100, ts="2025-09-01T10:00:00", note="test")
    new = add_transaction(trans, t)
    assert new is not trans
    assert new[-1].id == "tx_test"
    assert len(new) == len(trans) + 1

def test_update_budget_changes_limit():
    _, buds = load_seed(SEED)
    bid = buds[0].id
    new_limit = buds[0].limit + 111
    new_buds = update_budget(buds, bid, new_limit)
    assert any(b.limit == new_limit and b.id == bid for b in new_buds)
    assert buds[0].limit != new_limit

def test_account_balance_reduce_sum():
    trans, _ = load_seed(SEED)
    bal = account_balance(trans, "a2")
    manual = sum(t.amount for t in trans if t.account_id == "a2")
    assert bal == manual

def test_immutability_of_transaction_objects():
    trans, _ = load_seed(SEED)
    t = trans[0]
    try:
        t.amount = 999
        mutated = True
    except Exception:
        mutated = False
    assert mutated is False
