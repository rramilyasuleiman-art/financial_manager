import sys
from pathlib import Path

# ✅ Добавляем путь к корню проекта (чтобы core/ было видно)
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from core.domain import Account, Category, Transaction, Budget
from core.transforms import load_seed, account_balance

# Загружаем данные
accounts, categories, transactions, budgets = load_seed("data/seed.json")

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Financial Manager", layout="wide")
st.title("💰 Financial Manager")

menu = ["Overview", "Data", "Functional Core", "Reports", "About"]
choice = st.sidebar.radio("Меню", menu)

if choice == "Overview":
    st.header("📊 Обзор")
    st.write(f"Счета: {len(accounts)}")
    st.write(f"Категории: {len(categories)}")
    st.write(f"Транзакции: {len(transactions)}")
    st.write(f"Бюджеты: {len(budgets)}")

    total_balance = sum(account_balance(transactions, acc.id) for acc in accounts)
    st.metric("💵 Суммарный баланс", f"{total_balance} KZT")

elif choice == "Data":
    st.header("📂 Данные")
    st.subheader("Счета")
    st.write(accounts)
    st.subheader("Категории")
    st.write(categories)
    st.subheader("Транзакции")
    st.write(transactions[:20])  # показываем только первые 20
    st.subheader("Бюджеты")
    st.write(budgets)

elif choice == "Functional Core":
    st.header("⚙️ Функциональное ядро")
    st.code(
        """
def add_transaction(trans: tuple[Transaction,...], t:Transaction) -> tuple[Transaction,...]:
    return trans + (t,)
"""
    )

elif choice == "Reports":
    st.header("📑 Отчёты")
    st.info("Здесь будут отчёты по бюджету и категориям.")

elif choice == "About":
    st.header("ℹ️ О проекте")
    st.write("Учебный проект: Финансовый менеджер (Streamlit + функциональное программирование).")
