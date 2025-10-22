from typing import Tuple
from .domain import Category, Transaction

def by_category(cat_id: str):
    # closure returning predicate
    return lambda t: t.cat_id == cat_id

def by_date_range(start: str, end: str):
    return lambda t: start <= t.ts <= end

def by_amount_range(min_a: int, max_a: int):
    return lambda t: min_a <= t.amount <= max_a
from typing import Tuple
from core.domain import Category

def flatten_categories(cats: Tuple[Category, ...], root: str) -> Tuple[Category, ...]:
    lookup = {c.id: c for c in cats}
    children = {}
    for c in cats:
        children.setdefault(c.parent_id, []).append(c)

    result = []

    def dfs(cid):
        for child in children.get(cid, []):
            result.append(child)
            dfs(child.id)

    if root == "null":
        # создаём виртуальный корень
        virtual_root = Category(id="null", name="Root", parent_id=None, type="virtual")
        result.append(virtual_root)
        # добавляем все категории без родителя
        for c in cats:
            if c.parent_id in (None, "null", ""):
                result.append(c)
                dfs(c.id)
    elif root in lookup:
        result.append(lookup[root])
        dfs(root)
    else:
        dfs(root)

    return tuple(result)



def sum_expenses_recursive(cats: Tuple[Category, ...], trans: Tuple[Transaction, ...], root_id: str) -> int:
    # collects ids recursively and sums negative amounts
    flat = flatten_categories(cats, root_id)
    ids = {c.id for c in flat}
    ids.add(root_id)
    # recursion to sum by splitting set into head/tail (demonstrative recursion)
    related = [t.amount for t in trans if t.cat_id in ids and t.amount < 0]

    def rec(lst):
        if not lst:
            return 0
        if len(lst) == 1:
            return lst[0]
        return lst[0] + rec(lst[1:])
    return rec(related)