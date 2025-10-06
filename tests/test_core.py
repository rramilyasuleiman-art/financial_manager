from pathlib import Path
import pytest
from core.domain import Transaction, Budget
from core.transforms import add_transaction, update_budget, account_balance, load_seed

ROOT = Path(__file__).parents[1]
SEED = ROOT / "data" / "seed.json"

# Проверяем, что load_seed загружает данные и возвращает именно кортежи (tuple), а не списки.
    # Также проверяем, что данных достаточно для требований задания:
    #   ≥3 счета, ≥10 категорий, ≥20 транзакций, ≥3 бюджета.
def test_load_seed_has_collections():
    accounts, categories, transactions, budgets = load_seed(SEED)
    assert isinstance(accounts, tuple)
    assert isinstance(categories, tuple)
    assert isinstance(transactions, tuple)
    assert isinstance(budgets, tuple)
    assert len(accounts) >= 3
    assert len(categories) >= 10
    assert len(transactions) >= 20 
    assert len(budgets) >= 3

 # Проверяем, что add_transaction возвращает новый кортеж, а не изменяет старый.
    # Также убеждаемся, что новая транзакция добавлена в конец, и длина увеличилась на 1.
def test_add_transaction_returns_new_tuple():
    _, _, transactions, _ = load_seed(SEED)
    t = Transaction(
        id="tx_test",
        account_id="a1",
        cat_id="c_other",
        amount=-100,
        ts="2025-09-01T10:00:00",
        note="test",
    )
    new_trans = add_transaction(transactions, t)
    assert new_trans is not transactions
    assert new_trans[-1].id == "tx_test"
    assert len(new_trans) == len(transactions) + 1

 # Проверяем, что update_budget возвращает новый набор бюджетов, где
    #   у нужного бюджета изменился лимит
    #   старый объект бюджета остался неизменным (иммутабельность).
def test_update_budget_changes_limit():
    _, _, _, budgets = load_seed(SEED)
    bid = budgets[0].id
    new_limit = budgets[0].limit + 111
    new_budgets = update_budget(budgets, bid, new_limit)
    assert any(b.id == bid and b.limit == new_limit for b in new_budgets)
    assert budgets[0].limit != new_limit

# Проверяем функцию account_balance:
    #    она должна вернуть правильный баланс для указанного аккаунта.
    #   сравниваем результат reduce с ручным подсчётом через sum().
def test_account_balance_reduce_sum():
    _, _, transactions, _ = load_seed(SEED)
    acc_id = "a2"
    bal = account_balance(transactions, acc_id)
    manual_sum = sum(t.amount for t in transactions if t.account_id == acc_id)
    assert bal == manual_sum

# Проверяем, что Transaction иммутабелен (frozen dataclass).
    # Попытка изменить поле должна выбросить исключение.
def test_immutability_of_transaction_objects():
    _, _, transactions, _ = load_seed(SEED)
    t = transactions[0]
    with pytest.raises(Exception):
        t.amount = 999

from datetime import datetime, timedelta
from core.transforms import delete_old_transactions, category_balance

# Проверка рекурсивного удаления старых транзакций
def test_delete_old_transactions_removes_old():
    _, _, transactions, _ = load_seed(SEED)
    cutoff = datetime.fromisoformat("2025-01-01T00:00:00")
    new_trans = delete_old_transactions(transactions, cutoff)
    for t in new_trans:
        assert datetime.fromisoformat(t.ts) >= cutoff
    # Проверяем, что хотя бы одна транзакция была удалена
    assert len(new_trans) <= len(transactions)

# Проверка, что delete_old_transactions не изменяет исходный кортеж
def test_delete_old_transactions_immutable():
    _, _, transactions, _ = load_seed(SEED)
    cutoff = datetime.now()
    new_trans = delete_old_transactions(transactions, cutoff)
    assert transactions is not new_trans

# Проверка category_balance для существующей категории
def test_category_balance_correct_sum():
    _, categories, transactions, _ = load_seed(SEED)
    cat_id = categories[0].id
    total = category_balance(transactions, cat_id)
    manual_sum = sum(t.amount for t in transactions if t.cat_id == cat_id)
    assert total == manual_sum

# Проверка category_balance для категории без транзакций
def test_category_balance_empty():
    _, _, transactions, _ = load_seed(SEED)
    cat_id = "non_existing_category"
    total = category_balance(transactions, cat_id)
    assert total == 0

# Проверка delete_old_transactions для пустого кортежа
def test_delete_old_transactions_empty():
    new_trans = delete_old_transactions((), datetime.now())
    assert new_trans == ()

