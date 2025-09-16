from __future__ import annotations
from functools import reduce
from typing import Tuple
import json
from core.domain import Account, Category, Transaction, Budget

Transactions = Tuple[Transaction, ...]
Budgets = Tuple[Budget, ...]

def load_seed(path: str) -> tuple[tuple[Account, ...], tuple[Category, ...], tuple[Transaction, ...], tuple[Budget, ...]]:
    """Загружает данные из seed.json и преобразует в кортежи доменных сущностей."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    accounts = tuple(Account(**a) for a in data["accounts"])
    categories = tuple(Category(**c) for c in data["categories"])
    transactions = tuple(Transaction(**t) for t in data["transactions"])
    budgets = tuple(Budget(**b) for b in data["budgets"])

    return accounts, categories, transactions, budgets
def add_transaction(trans: Transactions, t: Transaction) -> Transactions:
    return trans + (t,)

def update_budget(budgets: Budgets, bid: str, new_limit: int) -> Budgets:
    def _update(b: Budget):
        if b.id == bid:
            return Budget(id=b.id, cat_id=b.cat_id, limit=new_limit, period=b.period)
        return b
    return tuple(_update(b) for b in budgets)

def account_balance(trans: Transactions, acc_id: str) -> int:
    def _acc(sum_, t: Transaction):
        return sum_ + (t.amount if t.account_id == acc_id else 0)
    return reduce(_acc, trans, 0)
