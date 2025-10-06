from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class User:
    id: str
    username: str
    password: str
    is_admin: bool = False

@dataclass(frozen=True)
class Account:
    id: str
    username: str
    password: str
    balance: int = 0
    currency: str = "KZT"
    is_admin: bool = False

@dataclass(frozen=True)
class Category:
    id: str
    name: str
    parent_id: Optional[str]
    type: str

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
    user_id: str
    cat_id: str
    limit: int
    period: str

@dataclass(frozen=True)
class Event:
    id: str
    ts: str
    name: str
    payload: Dict[str, Any]
