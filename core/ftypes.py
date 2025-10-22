from typing import Callable, Generic, TypeVar, Optional, Tuple 
T = TypeVar("T")
E = TypeVar("E")

class Maybe(Generic[T]):
    def __init__(self, value: Optional[T]):
        self._v = value

    def is_some(self) -> bool:
        return self._v is not None

    def map(self, fn: Callable[[T], T]) -> 'Maybe':
        if self._v is None:
            return Maybe(None)
        return Maybe(fn(self._v))

    def bind(self, fn: Callable[[T], 'Maybe']) -> 'Maybe':
        if self._v is None:
            return Maybe(None)
        return fn(self._v)

    def get_or_else(self, default):
        return self._v if self._v is not None else default

class Either(Generic[E, T]):
    def __init__(self, left: Optional[E]=None, right: Optional[T]=None):
        self.left = left
        self.right = right

    @staticmethod
    def Right(v: T) -> 'Either':
        return Either(None, v)

    @staticmethod
    def Left(e: E) -> 'Either':
        return Either(e, None)

    def is_right(self) -> bool:
        return self.right is not None

    def map(self, fn: Callable[[T], T]) -> 'Either':
        if self.right is None:
            return self
        return Either.Right(fn(self.right))

    def bind(self, fn: Callable[[T], 'Either']) -> 'Either':
        if self.right is None:
            return self
        return fn(self.right)

    def get_or_else(self, default):
        return self.right if self.right is not None else default

# helpers required by the lab
def safe_category(cats: Tuple, cat_id: str) -> Maybe:
    cat = next((c for c in cats if c.id == cat_id), None)
    return Maybe(cat)

def validate_transaction(t, accs: Tuple, cats: Tuple) -> Either:
    acc = next((a for a in accs if a.id == t.account_id), None)
    if acc is None:
        return Either.Left({"error": "account_not_found"})
    cat = next((c for c in cats if c.id == t.cat_id), None)
    if cat is None:
        return Either.Left({"error": "category_not_found"})
    return Either.Right(t)

def check_budget(b, trans: Tuple) -> Either:
    spent = sum(abs(t.amount) for t in trans if t.cat_id == b.cat_id and t.amount < 0)
    if spent > b.limit:
        return Either.Left({"error": "over_budget", "spent": spent, "limit": b.limit})
    return Either.Right(b)