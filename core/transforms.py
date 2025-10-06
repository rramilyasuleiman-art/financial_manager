from __future__ import annotations
from functools import reduce
from typing import Tuple
import json
from core.domain import Account, Category, Transaction, Budget

Transactions = Tuple[Transaction, ...]
Budgets = Tuple[Budget, ...]
Accounts = Tuple[Account, ...]
Categories = Tuple[Category, ...]


def load_seed(path: str) -> Tuple[Accounts, Categories, Transactions, Budgets]:
    """Загружает данные из seed.json и преобразует в кортежи доменных сущностей."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    accounts = tuple(map(lambda a: Account(**a), data["accounts"]))
    categories = tuple(map(lambda c: Category(**c), data["categories"]))
    transactions = tuple(map(lambda t: Transaction(**t), data["transactions"]))
    budgets = tuple(map(lambda b: Budget(**b), data["budgets"]))

    return accounts, categories, transactions, budgets


def add_transaction(trans: Transactions, t: Transaction) -> Transactions:
    """Добавляет транзакцию в кортеж транзакций (иммутабельно)."""
    return trans + (t,)


def update_budget(budgets: Budgets, bid: str, new_limit: int) -> Budgets:
    """Обновляет лимит бюджета по id (иммутабельно)."""
    return tuple(
        Budget(
            id=b.id,
            user_id=b.user_id,   
            cat_id=b.cat_id,
            limit=new_limit,
            period=b.period
        ) if b.id == bid else b
        for b in budgets
    )


def account_balance(trans: Transactions, acc_id: str) -> int:
    """Возвращает текущий баланс счёта на основе транзакций."""
    filtered = filter(lambda t: t.account_id == acc_id, trans)
    amounts = map(lambda t: t.amount, filtered)
    return reduce(lambda total, x: total + x, amounts, 0)


def category_balance(trans: Transactions, cat_id: str) -> int:
    """Сумма всех транзакций по заданной категории (пример map/filter)."""
    filtered = filter(lambda t: t.cat_id == cat_id, trans)
    amounts = map(lambda t: t.amount, filtered)
    return reduce(lambda total, x: total + x, amounts, 0)


def save_seed(path: str, accounts: Accounts, categories: Categories, transactions: Transactions, budgets: Budgets) -> None:
    """Сохраняет данные обратно в seed.json."""
    data = {
        "accounts": list(map(lambda a: a.__dict__, accounts)),
        "categories": list(map(lambda c: c.__dict__, categories)),
        "transactions": list(map(lambda t: t.__dict__, transactions)),
        "budgets": list(map(lambda b: b.__dict__, budgets)),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

from datetime import datetime
from core.domain import Transaction

Transactions = tuple[Transaction, ...]

def delete_old_transactions(transactions: Transactions, cutoff_date: datetime) -> Transactions:
    """
    Рекурсивно удаляет транзакции старше cutoff_date.
    Возвращает новый кортеж транзакций.
    """
    if not transactions:
        return ()
    t = transactions[0]
    rest = delete_old_transactions(transactions[1:], cutoff_date)
    if datetime.fromisoformat(t.ts) < cutoff_date:
        return rest
    else:
        return (t,) + rest

