from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    username: str
    password: str
    role: str 

@dataclass(frozen=True)
class Account:
    id: str
    name: str
    balance: int
    currency: str
    user_id: str  

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
    user_id: str  
    cat_id: str
    amount: int
    ts: str
    note: str
    deleted: bool = False 

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
