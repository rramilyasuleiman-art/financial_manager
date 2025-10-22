import pytest
from core.recursion import by_category, by_date_range, by_amount_range, flatten_categories, sum_expenses_recursive
from core.transforms import load_seed

def test_closure_by_category():
    _, cats, trans, _ = load_seed("data/seed.json")
    pred = by_category("cat6")
    assert all(pred(t) == (t.cat_id == "cat6") for t in trans)

def test_closure_by_date_range():
    _, _, trans, _ = load_seed("data/seed.json")
    pred = by_date_range("2025-01-01T00:00:00", "2025-01-31T23:59:59")
    assert any(pred(t) for t in trans)

def test_closure_by_amount_range():
    _, _, trans, _ = load_seed("data/seed.json")
    pred = by_amount_range(-5000, 0)
    assert any(pred(t) for t in trans)
    
def test_flatten_categories_contains_descendants_and_root():
    _, cats, _, _ = load_seed("data/seed.json")
    flat = flatten_categories(cats, "null")

    # Проверяем, что виртуальный корень "null" действительно есть
    assert any(c.id == "null" for c in flat), "В списке нет виртуального корня 'null'"

    # Проверяем, что у хотя бы одной категории parent_id == "null"
    # (то есть она привязана к виртуальному корню)
    assert any(getattr(c, "parent_id", None) in (None, "null", "") or c.parent_id == "null" for c in flat if c.id != "null"), \
        "Нет ни одной категории, у которой родитель 'null'"

def test_sum_expenses_recursive_returns_int():
    _, cats, trans, _ = load_seed("data/seed.json")
    s = sum_expenses_recursive(cats, trans, "cat2")  # Расход
    assert isinstance(s, int)
