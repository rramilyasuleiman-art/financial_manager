from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Account:
    id: str
    name: str
    balance: int
    currency: str

@dataclass(frozen=True)
class Category:
    id: str
    name: str
    parent_id: Optional[str]
    type: str  # 'income' or 'expense'

@dataclass(frozen=True)
class Transaction:
    id: str
    account_id: str
    cat_id: str
    amount: int
    ts: str
    note: str

@dataclass(frozen=True)
class Budget:
    id: str
    cat_id: str
    limit: int
    period: str

@dataclass(frozen=True)
class Event:
    id: str
    ts: str
    name: str
    payload: dict
