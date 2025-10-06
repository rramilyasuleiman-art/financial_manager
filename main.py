import sys
from pathlib import Path
import streamlit as st
from datetime import datetime
from core.transforms import delete_old_transactions

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.domain import Account, Category, Transaction, Budget
from core.transforms import load_seed, account_balance, save_seed, add_transaction, update_budget

DATA_PATH = "data/seed.json"

# Загрузка данных
if "users" not in st.session_state:
    users, categories, transactions, budgets = load_seed(DATA_PATH)
    st.session_state["users"] = users
    st.session_state["categories"] = categories
    st.session_state["transactions"] = transactions
    st.session_state["budgets"] = budgets
    st.session_state["current_user"] = None

users = st.session_state["users"]
categories = st.session_state["categories"]
transactions = st.session_state["transactions"]
budgets = st.session_state["budgets"]


# Функции: замыкания и рекурсия

# Замыкание для фильтра транзакций
def transaction_filter(category=None, min_amount=None, max_amount=None, start_date=None, end_date=None):
    def filter_fn(transactions):
        filtered = []
        for t in transactions:
            if category and t.cat_id != category:
                continue
            if min_amount is not None and t.amount < min_amount:
                continue
            if max_amount is not None and t.amount > max_amount:
                continue
            if start_date and datetime.fromisoformat(t.ts) < start_date:
                continue
            if end_date and datetime.fromisoformat(t.ts) > end_date:
                continue
            filtered.append(t)
        return filtered
    return filter_fn

# Рекурсивная проверка превышения бюджета
def recursive_budget_check(budget_list, transaction_list):
    if not budget_list:
        return []
    b = budget_list[0]
    spent = sum(t.amount for t in transaction_list if t.cat_id == b.cat_id)
    exceeded = []
    if spent > b.limit:
        exceeded.append(b.cat_id)
    return exceeded + recursive_budget_check(budget_list[1:], transaction_list)

# Рекурсивное удаление старых транзакций
def delete_old_transactions(transactions, cutoff_date):
    if not transactions:
        return []
    t = transactions[0]
    rest = delete_old_transactions(transactions[1:], cutoff_date)
    if datetime.fromisoformat(t.ts) < cutoff_date:
        return rest
    else:
        return [t] + rest


# Авторизация

if st.session_state["current_user"] is None:
    st.set_page_config(page_title="Финансовый менеджер", layout="centered")
    st.title("🔐 Авторизация")

    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        user = next((u for u in users if u.username == username and u.password == password), None)
        if user:
            st.session_state["current_user"] = user
            st.success(f"Добро пожаловать, {user.username}!")
            st.rerun()
        else:
            st.error("❌ Неверный логин или пароль")
    st.stop()

current_user = st.session_state["current_user"]
st.set_page_config(page_title="Финансовый менеджер", layout="wide")
st.title("💰 Финансовый менеджер")


# Меню

menu = ["Обзор", "Данные", "Действия"]
if getattr(current_user, "is_admin", False):
    menu.append("Администрирование")

choice = st.sidebar.radio("Меню", menu)

# Ограничение данных для обычного пользователя
if not getattr(current_user, "is_admin", False):
    transactions = [t for t in transactions if t.account_id == current_user.id]
    budgets = [b for b in budgets if getattr(b, "user_id", None) == current_user.id]


# Меню: Обзор

if choice == "Обзор":
    st.header("📊 Обзор")
    st.write(f"👤 Пользователи: {len(users)}")
    st.write(f"📂 Категории: {len(categories)}")
    st.write(f"💸 Транзакции: {len(transactions)}")
    st.write(f"📑 Бюджеты: {len(budgets)}")

    if getattr(current_user, "is_admin", False):
        total_balance = sum(account_balance(transactions, u.id) for u in users)
    else:
        total_balance = account_balance(transactions, current_user.id)
    st.metric("💵 Баланс", f"{total_balance} KZT")


# Меню: Данные
elif choice == "Данные":
    st.header("📂 Данные")
    st.subheader("👤 Пользователь")
    st.table([current_user.__dict__])
    st.subheader("📂 Категории")
    st.table([c.__dict__ for c in categories])
    st.subheader("💸 Транзакции (первые 20)")
    st.dataframe([t.__dict__ for t in transactions[:20]])
    st.subheader("📑 Бюджеты")
    st.table([b.__dict__ for b in budgets])

# Меню: Действия
elif choice == "Действия":
    st.header("⚙️ Действия")

    # Добавление транзакции 
    st.subheader("➕ Добавить транзакцию")
    cat_id = st.selectbox("Выберите категорию", [c.id for c in categories])
    amount = st.number_input("Сумма", value=0)
    note = st.text_input("Заметка")

    if st.button("Добавить"):
        new_t = Transaction(
            id=f"t{len(st.session_state['transactions']) + 1}",
            account_id=current_user.id,
            cat_id=cat_id,
            amount=amount,
            ts=datetime.now().isoformat(timespec="seconds"),
            note=note,
        )
        st.session_state["transactions"] = add_transaction(st.session_state["transactions"], new_t)
        save_seed(
            DATA_PATH,
            st.session_state["users"],
            st.session_state["categories"],
            st.session_state["transactions"],
            st.session_state["budgets"],
        )
        st.success("✅ Транзакция добавлена и сохранена в файл!")

    #Фильтр транзакций 
    st.subheader("🔎 Фильтр транзакций")
    filter_cat = st.selectbox("Фильтровать по категории", [None] + [c.id for c in categories])
    min_amount = st.number_input("Минимальная сумма", value=0)
    max_amount = st.number_input("Максимальная сумма", value=0)
    if st.button("Применить фильтр"):
        filtered = transaction_filter(
            category=filter_cat if filter_cat is not None else None,
            min_amount=min_amount if min_amount != 0 else None,
            max_amount=max_amount if max_amount != 0 else None
        )(transactions)
        st.dataframe([t.__dict__ for t in filtered])

    # Проверка бюджета 
    st.subheader("⚠️ Проверка превышения бюджета")
    if st.button("Проверить бюджет"):
        exceeded = recursive_budget_check(budgets, transactions)
        if exceeded:
            st.warning(f"Превышен бюджет по категориям: {', '.join(exceeded)}")
        else:
            st.success("Бюджет в норме!")

    # Удаление старых транзакций 
    st.subheader("🗑 Удаление старых транзакций")
    cutoff_str = st.date_input("Удалить все транзакции до даты")
    if st.button("Очистить"):
        cutoff_date = datetime.combine(cutoff_str, datetime.min.time())
        old_count = len(st.session_state["transactions"])
        st.session_state["transactions"] = delete_old_transactions(
            st.session_state["transactions"], cutoff_date
        )
        deleted_count = old_count - len(st.session_state["transactions"])
        save_seed(
            DATA_PATH,
            st.session_state["users"],
            st.session_state["categories"],
            st.session_state["transactions"],
            st.session_state["budgets"],
        )
        st.success(f"✅ Удалено {deleted_count} транзакций до {cutoff_date.date()}!")

# Меню: Администрирование

elif choice == "Администрирование" and getattr(current_user, "is_admin", False):
    st.header("👑 Администрирование")
    selected_uid = st.selectbox("Выберите пользователя", [u.id for u in users])
    selected_user = next(u for u in users if u.id == selected_uid)
    st.subheader(f"Данные пользователя: {selected_user.username}")
    st.table([selected_user.__dict__])
    user_transactions = [t.__dict__ for t in transactions if t.account_id == selected_uid]
    st.subheader("Транзакции")
    st.dataframe(user_transactions)
    user_budgets = [b.__dict__ for b in budgets if getattr(b, "user_id", None) == selected_uid]
    st.subheader("Бюджеты")
    st.table(user_budgets)
