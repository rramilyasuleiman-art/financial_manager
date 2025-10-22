import json
from functools import reduce, lru_cache
from typing import Tuple
from core.domain import User, Account, Category, Transaction, Budget

# ----------------- Users -----------------
@lru_cache
def load_users(path: str) -> Tuple[User, ...]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return tuple(User(**u) for u in data.get("users", []))

def authenticate(users: Tuple[User, ...], username: str, password: str):
    for u in users:
        if u.username == username and u.password == password:
            return u
    return None

# ----------------- Seed -----------------
def load_seed(path: str) -> Tuple[Tuple[Account, ...], Tuple[Category, ...], Tuple[Transaction, ...], Tuple[Budget, ...]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    accounts = tuple(Account(**a) for a in data.get("accounts", []))
    categories = tuple(Category(**c) for c in data.get("categories", []))
    transactions = tuple(Transaction(**t) for t in data.get("transactions", []))
    budgets = tuple(Budget(**b) for b in data.get("budgets", []))
    return accounts, categories, transactions, budgets

# ----------------- Functional Core -----------------
def add_transaction(trans: Tuple[Transaction, ...], t: Transaction) -> Tuple[Transaction, ...]:
    # Добавляем новую транзакцию в кортеж
    return trans + (t,)

def update_budget(budgets: Tuple[Budget, ...], bid: str, new_limit: int) -> Tuple[Budget, ...]:
    return tuple(
        Budget(
            b.id,
            b.cat_id,
            new_limit if b.id == bid else b.limit,
            b.period
        )
        for b in budgets
    )

def account_balance(trans: Tuple[Transaction, ...], acc_id: str) -> int:
    filtered = tuple(filter(lambda t: t.account_id == acc_id, trans))
    return reduce(lambda acc, t: acc + t.amount, filtered, 0)
