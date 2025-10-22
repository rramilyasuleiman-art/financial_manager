import pytest
from core.ftypes import Maybe, Either, safe_category, validate_transaction, check_budget
from core.transforms import load_seed
from core.domain import Transaction

# Test 1: Tests how Maybe works with map, bind, and get_or_else
def test_maybe_map_bind_get_or_else():
    m = Maybe(10)  # create Maybe with value 10
    # map adds 5 → gives 15, bind multiplies by 2 → gives 30, then get_or_else returns 30
    assert m.map(lambda x: x + 5).bind(lambda x: Maybe(x * 2)).get_or_else(0) == 30
    # if Maybe(None), get_or_else returns default value (5)
    assert Maybe(None).get_or_else(5) == 5

# Test 2: Tests how Either (Right) works with map and get_or_else
def test_either_right_map_bind_get_or_else():
    e = Either.Right(7)  # create Right with value 7
    # map adds 1 → result becomes 8, get_or_else returns 8
    assert e.map(lambda x: x + 1).get_or_else(0) == 8

# Test 3: Tests safe_category (returns Maybe depending on whether category exists)
def test_safe_category_some_and_none():
    _, cats, _, _ = load_seed("data/seed.json")  # load data
    maybe = safe_category(cats, cats[0].id)      # valid category id
    assert maybe.is_some()                       # should be found → True
    maybe_none = safe_category(cats, "missing")  # invalid id
    assert not maybe_none.is_some()              # should not be found → False

# Test 4: Tests validate_transaction when account does NOT exist
def test_validate_transaction_missing_account():
    accs, cats, trans, buds = load_seed("data/seed.json")
    # Create fake transaction: account_id="noacc" doesn’t exist
    # Important: include user_id in correct position ("admin")
    t = Transaction("x", "noacc", "admin", cats[0].id, -100, "2025-01-01", "")
    res = validate_transaction(t, accs, cats)
    # Should return Either.Left with error "account_not_found"
    assert res.left is not None and "account_not_found" in res.left.get("error", "")

# Test 5: Tests check_budget function (if spending exceeds limit or not)
def test_check_budget_over_and_ok():
    accs, cats, trans, buds = load_seed("data/seed.json")
    b = buds[0]                                  # take the first budget
    res = check_budget(b, trans)                 # validate against transactions
    assert isinstance(res, Either)               # result must always be Either type
