import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json
import streamlit as st
from copy import replace
import matplotlib.pyplot as plt
from collections import defaultdict, OrderedDict

# ----------------- Paths -----------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ----------------- Imports -----------------
from core.transforms import load_seed, add_transaction, update_budget, account_balance, load_users, authenticate
from core.domain import User, Transaction, Account, Category, Budget
from core.recursion import flatten_categories, sum_expenses_recursive, by_category, by_date_range, by_amount_range
from core.memo import forecast_expenses_timed
from core.ftypes import validate_transaction, check_budget, Maybe, Either

# ----------------- Streamlit config -----------------
st.set_page_config(page_title="Financial Manager", layout="wide")
st.title("💼 Financial Manager")

# ----------------- Load data -----------------
accounts, categories, transactions, budgets = load_seed(str(ROOT / "data/seed.json"))
users = load_users(str(ROOT / "data/seed.json"))

# ----------------- Session state -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "transactions" not in st.session_state:
    st.session_state.transactions = transactions  # инициализация один раз

# ----------------- Authentication -----------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Sign In"):
        user = authenticate(users, username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.transactions = transactions
            st.success(f"Welcome, {user.username} ({user.role})")
        else:
            st.error("❌ Invalid username or password")

# ----------------- Main app -----------------
if st.session_state.logged_in and st.session_state.user is not None:
    user = st.session_state.user

    # --- Фильтрация данных по пользователю ---
    if user.role == "admin":
        user_accounts = accounts
        visible_transactions = st.session_state.transactions
    else:
        user_accounts = [a for a in accounts if getattr(a, "user_id", None) == user.username]
        visible_transactions = [t for t in st.session_state.transactions if t.account_id in [a.id for a in user_accounts]]

    # --- Боковое меню ---
    st.sidebar.success(f"Logged in as {user.username} ({user.role})")
    menu_items = ["Overview", "Data", "Functional Core", "Pipelines", "Reports"]
    choice = st.sidebar.radio("📋 Menu", menu_items)

    # ----------------- Overview -----------------
    if choice == "Overview":
        st.header("📊 Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accounts", len(user_accounts))
        col2.metric("Categories", len(categories))
        col3.metric("Transactions", len(visible_transactions))
        total_balance = sum(a.balance for a in user_accounts) + sum(t.amount for t in visible_transactions)
        col4.metric("Total Balance", total_balance)

    # ----------------- Data -----------------
    elif choice == "Data":
        st.header("📁 Data Explorer")
        st.subheader("Accounts")
        st.table([a.__dict__ for a in user_accounts])
        st.subheader("Categories")
        st.table([c.__dict__ for c in categories])
        st.subheader("Transactions (first 20)")
        st.table([t.__dict__ for t in visible_transactions[:20]])

    # ----------------- Functional Core -----------------
    elif choice == "Functional Core":
        st.header("➕ Add Transaction")

        if not user_accounts:
            st.warning("У вас пока нет счетов. Обратитесь к администратору для их создания.")
        else:
            acc = st.selectbox("💳 Account", user_accounts, format_func=lambda a: a.name)
            cat = st.selectbox("📂 Category", categories, format_func=lambda c: c.name)
            amount = st.number_input("💰 Amount", value=0, step=100)
            note = st.text_input("📝 Note", placeholder="Например: продукты, зарплата...")

            signed_amount = abs(int(amount)) if "income" in cat.id.lower() or "income" in cat.name.lower() else -abs(int(amount))

            if st.button("Add Transaction"):
                t = Transaction(
                    id=str(uuid4()),
                    account_id=acc.id,
                    user_id=user.username,
                    cat_id=cat.id,
                    amount=signed_amount,
                    ts=datetime.now().isoformat(timespec="seconds"),
                    note=note,
                    deleted=False
                )
                st.session_state.transactions = add_transaction(st.session_state.transactions, t)

                # Обновляем seed.json
                seed_path = ROOT / "data/seed.json"
                with open(seed_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["transactions"].append(t.__dict__)
                with open(seed_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                st.success("✅ Transaction added and saved successfully!")
                with st.expander("📜 View last transaction"):
                    st.json(t.__dict__)

        # --- Просмотр и удаление ---
        st.divider()
        st.subheader("💼 Your Transactions")

        if user.role == "admin":
            user_transactions = st.session_state.transactions
        else:
            user_transactions = [t for t in st.session_state.transactions if t.user_id == user.username and not t.deleted]

        if user_transactions:
            selected = st.selectbox(
                "Выберите транзакцию для просмотра/удаления:",
                user_transactions[::-1],
                format_func=lambda t: f"{t.note or '(без заметки)'} — {t.amount} ({t.ts})"
            )
            with st.expander("📄 Детали транзакции", expanded=True):
                st.markdown(f"""
                    **ID:** {selected.id}  
                    **Account:** {selected.account_id}  
                    **User:** {selected.user_id}  
                    **Category:** {selected.cat_id}  
                    **Amount:** {selected.amount}  
                    **Timestamp:** {selected.ts}  
                    **Note:** {selected.note}  
                    **Deleted:** {"Yes" if selected.deleted else "No"}  
                    """)

            if not selected.deleted:
                if st.button("🗑️ Удалить транзакцию"):
                    deleted_tr = replace(selected, deleted=True)
                    st.session_state.transactions = [deleted_tr if t.id == selected.id else t for t in st.session_state.transactions]

                    # Обновляем seed.json
                    seed_path = ROOT / "data/seed.json"
                    with open(seed_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for idx, tr in enumerate(data["transactions"]):
                        if tr["id"] == selected.id:
                            data["transactions"][idx]["deleted"] = True
                            break
                    with open(seed_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)

                    st.warning("🚫 Transaction marked as deleted (visible only to admin).")
            else:
                st.info("⚠️ Эта транзакция уже помечена как удалённая.")

        else:
            st.info("У вас пока нет транзакций.")
    
        # ----------------- Pipelines (Лаба 2+3) — улучшенный -----------------
    elif choice == "Pipelines":
        import matplotlib.pyplot as plt
        from datetime import datetime

        st.header("🔄 Data Filters & Recursive Reports")
        st.markdown("Примените фильтры для анализа транзакций и создайте рекурсивный отчёт по категориям.")

        # --- Панель фильтров ---
        with st.expander("🔍 Фильтры", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                sel_cat = st.selectbox(
                    "📂 Категория (опционально)",
                    [None] + [c for c in categories],
                    format_func=lambda c: c.name if c else "— Все категории —"
                )
            with col2:
                sel_from = st.date_input("📅 С (начало периода)", value=None)
            with col3:
                sel_to = st.date_input("📅 По (конец периода)", value=None)

            min_amt = st.number_input("💰 Мин. сумма", value=-1000000, step=100)
            max_amt = st.number_input("💰 Макс. сумма", value=1000000, step=100)

            # Кнопка фильтрации
            apply_filter = st.button("Применить фильтры")

        # --- Построение фильтров ---
        def parse_ts(ts: str):
            """Безопасное преобразование строки времени."""
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                try:
                    return datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                except Exception:
                    return None

        filtered = visible_transactions

        if apply_filter:
            # По категории
            if sel_cat:
                filtered = [t for t in filtered if getattr(t, "cat_id", None) == sel_cat.id]

            # По диапазону дат
            if sel_from and sel_to:
                filtered = [
                    t for t in filtered
                    if (dt := parse_ts(getattr(t, "ts", "")))
                    and sel_from <= dt.date() <= sel_to
                ]

            # По сумме
            filtered = [t for t in filtered if min_amt <= t.amount <= max_amt]

        # --- Результаты фильтра ---
        st.divider()
        st.subheader("📋 Результаты фильтрации")

        st.info(f"Найдено транзакций: **{len(filtered)}**")

        if filtered:
            st.dataframe(
                [
                    {
                        "ID": t.id,
                        "Account": t.account_id,
                        "Category": t.cat_id,
                        "Amount": t.amount,
                        "Date": t.ts,
                        "Note": t.note,
                    }
                    for t in filtered[:50]
                ],
                use_container_width=True
            )

            # --- Мини-график сумм по датам ---
            try:
                dates = [parse_ts(t.ts) for t in filtered if parse_ts(t.ts)]
                amounts = [t.amount for t in filtered if parse_ts(t.ts)]
                if dates:
                    st.subheader("📈 Динамика транзакций")
                    fig, ax = plt.subplots()
                    ax.plot(dates, amounts, marker="o", linestyle="-")
                    ax.set_xlabel("Дата")
                    ax.set_ylabel("Сумма")
                    ax.set_title("График фильтрованных транзакций")
                    ax.grid(True)
                    plt.xticks(rotation=30)
                    st.pyplot(fig)
            except Exception as e:
                st.warning(f"⚠ Ошибка при построении графика: {e}")

        else:
            st.warning("Транзакции не найдены по заданным условиям.")

        # --- Рекурсивный отчёт ---
        st.divider()
        st.subheader("🧮 Recursive Report by Category")

        root_cat = st.selectbox(
            "Выберите корневую категорию",
            categories,
            format_func=lambda c: f"{c.name} ({c.id})"
        )

        if st.button("Сгенерировать отчёт"):
            try:
                flat_cats = flatten_categories(tuple(categories), root_cat.id)
                total = sum_expenses_recursive(flat_cats, visible_transactions, root_cat.id)
                st.success(f"💵 Total expenses recursively under **{root_cat.name}**: {total}")

                st.json([c.__dict__ for c in flat_cats], expanded=False)
            except Exception as e:
                st.error(f"Ошибка при рекурсивном отчёте: {e}")

        # ----------------- Reports (Лаба 3+4) — улучшенный -----------------
    elif choice == "Reports":
        import calendar
        from datetime import datetime
        from collections import defaultdict, OrderedDict
        import matplotlib.pyplot as plt

        st.header("📈 Reports & Forecast")
        st.markdown("Анализ и прогноз расходов по выбранной категории (по месяцам).")

        # --- Список категорий: можно ограничить категориями расходов ---
        # Покажем сначала только expense категории (чтобы прогноз был про расходы),
        # но оставим опцию показать всё.
        show_all = st.checkbox("Показывать все категории (включая доходы)", value=False)
        if show_all:
            cat_list = categories
        else:
            cat_list = [c for c in categories if getattr(c, "type", "").lower() != "income"]

        # Выбор категории (показываем человекочитаемые имена)
        cat = st.selectbox("Выберите категорию для отчёта", cat_list, format_func=lambda c: f"{c.name} ({c.id})")

        # период в месяцах для прогноза/анализа
        period = st.slider("Период для прогноза (месяцев, сколько последних месяцев учитывать)", 1, 24, 6)

        # --- Собираем ежемесячные суммы для выбранной категории ---
        def parse_ts(ts):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                # если формат другой — пробуем обрезать или вернуть None
                try:
                    return datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                except Exception:
                    return None

        monthly = defaultdict(int)  # ключ: (год, месяц) -> сумма
        for t in visible_transactions:
            try:
                if getattr(t, "cat_id", None) != cat.id:
                    continue
                dt = parse_ts(getattr(t, "ts", ""))
                if not dt:
                    continue
                key = (dt.year, dt.month)
                monthly[key] += t.amount
            except Exception:
                continue

        # Если нет данных — показываем подсказку
        if not monthly:
            st.info("Нет транзакций по выбранной категории в видимой выборке.")
        else:
            # Сортируем месяца по времени
            sorted_keys = sorted(monthly.keys())
            # Превращаем в OrderedDict для стабильности отображения
            monthly_ordered = OrderedDict((k, monthly[k]) for k in sorted_keys)

            # Возьмём последние N месяцев (period)
            last_keys = sorted_keys[-period:]
            labels = [f"{k[0]}-{k[1]:02d}" for k in last_keys]
            values = [monthly[k] for k in last_keys]

            # Простая статистика
            total = sum(values)
            avg = total / len(values) if values else 0
            median = sorted(values)[len(values)//2] if values else 0

            # Получим прогноз из cached-функции (твоя функция)
            try:
                forecast_val, ms = forecast_expenses_timed(cat.id, visible_transactions, period)
            except Exception as e:
                forecast_val, ms = None, None

            # Отображение ключевых метрик
            col1, col2, col3 = st.columns(3)
            col1.metric("Период (месяцев)", f"{len(values)}")
            col2.metric("Сумма за выбранный период", f"{total}")
            col3.metric("Среднее / мес", f"{avg:.2f}")

            if forecast_val is not None:
                st.info(f"Прогноз (cached) для следующего периода: {forecast_val} (вычислено за {ms:.3f} ms)")

            # Таблица с месяцами
            st.subheader("Детали по месяцам")
            rows = [{"month": labels[i], "amount": values[i]} for i in range(len(labels))]
            st.table(rows)

            # --- График (matplotlib) ---
            st.subheader("График по месяцам")
            fig, ax = plt.subplots()
            ax.plot(labels, values, marker="o")  # не указываем цвета
            ax.set_title(f"Monthly sums — {cat.name}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            ax.grid(True)
            plt.xticks(rotation=30)
            st.pyplot(fig)

            # --- Простейший тренд / прогноз на основе среднего ---
            st.subheader("Простой прогноз (на основе среднего)")
            next_period_estimate = avg
            st.write(f"Оценка на следующий месяц (по среднему): **{next_period_estimate:.2f}**")

            # Кнопка экспортировать CSV (последние N месяцев)
            if st.button("Экспортировать данные (CSV)"):
                import io, csv
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                writer.writerow(["month", "amount"])
                for r in rows:
                    writer.writerow([r["month"], r["amount"]])
                st.download_button("Скачать CSV", data=buffer.getvalue(), file_name=f"report_{cat.id}.csv", mime="text/csv")

        st.caption("Подсказка: если хотите прогнозы по доходам — отметьте 'Показывать все категории'.")

