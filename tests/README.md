# 💰 Financial Manager (Functional Programming Project)

## 🧭 Navigation

* [Overview](#-overview)
* [Project Structure](#-project-structure)
* [Installation & Setup](#-installation--setup)
* [How to Run the App](#-how-to-run-the-app)
* [Laboratory Works](#-laboratory-works)

  * [Lab 1 – Pure Functions & HOF](#lab-1--pure-functions--hof)
  * [Lab 2 – Closures & Recursion](#lab-2--closures--recursion)
  * [Lab 3 – Advanced Recursion & Memoization](#lab-3--advanced-recursion--memoization)
  * [Lab 4 – Functional Patterns (Maybe / Either)](#lab-4--functional-patterns-maybe--either)
* [Testing](#-testing)
* [Code Style & Linting](#-code-style--linting)
* [Team](#-team)

---

## 📘 Overview

**Financial Manager** is a Streamlit-based application built to demonstrate **functional programming principles** in Python.
It allows users to:

* Track transactions (income & expenses)
* Categorize financial operations
* Forecast future expenses using recursion and memoization
* Validate and process data safely with functional error-handling types (`Maybe`, `Either`)

This project was developed as part of a series of **Functional Programming labs (1–4)**.

---

## 🗂 Project Structure

```
financial_manager/
│
├── app/
│   └── main.py                # Streamlit interface (entry point)
│
├── core/
│   ├── domain.py              # Core domain models (Transaction, Budget, Category)
│   ├── ftypes.py              # Functional types (Maybe, Either, etc.)
│   ├── memo.py                # Memoization & recursive expense forecasting
│   ├── transforms.py          # Data transformations and seed loading
│
├── data/
│   └── seed.json              # Initial dataset for testing
│
├── tests/
│   └── test_core.py           # Unit tests (pytest)
│
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

---

## ⚙️ Installation & Setup

**Python version:** 3.13+

1. Clone or download the repository:

   ```
   git clone https://github.com/yourusername/financial_manager.git
   cd financial_manager
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. (Optional) Format and lint the code:

   ```
   black .
   ruff check .
   ```

---

## ▶️ How to Run the App

To start the Streamlit interface:

```
streamlit run app/main.py
```

Then open the local URL printed in the terminal (usually [http://localhost:8501](http://localhost:8501)).

---

## 🧩 Laboratory Works

### **Lab 1 – Pure Functions & HOF**

> *Goal:* Introduce functional programming concepts in Python.

* Implemented **pure functions** and **immutability**.
* Used **higher-order functions** like `map()`, `filter()`, and `reduce()`.
* Focused on transforming immutable data structures for transactions and budgets.

---

### **Lab 2 – Closures & Recursion**

> *Goal:* Use closures and recursive techniques for hierarchical data.

* Implemented recursive category traversal (`flatten_categories`).
* Created `sum_expenses_recursive` for calculating total expenses.
* Demonstrated **closure-based** accumulation for dynamic calculations.

---

### **Lab 3 – Advanced Recursion & Memoization**

> *Goal:* Optimize recursive algorithms and add time tracking.

* Implemented **memoization** to speed up expense forecasting.
* Added **timed recursion** (`forecast_expenses_timed`) for performance measurement.
* Ensured recursion depth and cache logic work efficiently.

---

### **Lab 4 – Functional Patterns (Maybe / Either)**

> *Goal:* Implement safe error handling using functional monads.

* Created functional types:

  * `Maybe` (safe optional value)
  * `Either` (error or valid result)
* Added `safe_category`, `validate_transaction`, and `check_budget` functions.
* Used **unit tests (pytest)** to verify correctness and error handling.

---

## 🧪 Testing

Run all tests using:

```
pytest -v
```

Example coverage:

* ✅ `Maybe` / `Either` operations
* ✅ Safe category retrieval
* ✅ Transaction validation
* ✅ Budget limit checks

---

## 🧹 Code Style & Linting

Format code:

```
black .
```

Check for style issues:

```
ruff check .
```

---

## 👥 Team

| Name                   | Role                                        |
| ---------------------- | ------------------------------------------- |
| **Сулейманова Рамиля** | Developer                                   |
| **Серикказы Арсен**    | Developer                                   |

---
