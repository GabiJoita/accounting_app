import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


def setup_db():
    """
        This function ensures the database is initialized and ready for storing
        transaction records when the app is started.
    """
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY,
                        customer_supplier TEXT,
                        type TEXT NOT NULL,
                        description TEXT,
                        price REAL NOT NULL,
                        vat REAL NOT NULL,
                        total REAL NOT NULL,
                        date TEXT,
                        category TEXT
                      )''')
    conn.commit()
    conn.close()


def add_transaction(cst_spl, trs_type, dsc, prc, vt, ttl, dt, ctg):
    """
        create this function
        to convert your input data into
        transaction
    """
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO transactions (customer_supplier, type,
                    description, price, vat, total, date, category)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (cst_spl, trs_type, dsc, prc, vt, ttl, dt, ctg))
    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def calculate_balance():
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM transactions WHERE type='income'")
    income_st = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(total) FROM transactions WHERE type='expense'")
    expense_st = cursor.fetchone()[0] or 0
    balance_st = income_st - expense_st
    conn.close()
    return income_st, expense_st, balance_st


def plot_transactions():
    conn = sqlite3.connect("accounting.db")
    df = pd.read_sql_query("SELECT type, SUM(total)"
                           " as amount FROM transactions GROUP BY type", conn)
    conn.close()
    fig = px.bar(df, x='type', y='amount', title="Income vs Expense", color='type',
                 labels={'type': 'Transaction Type', 'amount': 'Total Amount'},
                 color_discrete_map={'income': 'green', 'expense': 'red'})
    st.plotly_chart(fig)


st.title("Accounting Web Application")

setup_db()

with st.form("transaction_form"):
    st.subheader("Add New Transaction")
    customer_supplier = st.text_input("Customer/Supplier")
    transaction_type = st.selectbox("Transaction Type", ["income", "expense"])
    description = st.text_input("Description")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    vat_rate = st.selectbox("VAT Rate (%)", [19, 9, 0])
    date = st.date_input("Date")
    category = st.text_input("Category")

    vat = price * (vat_rate / 100)
    total = price + vat
    st.write(f"Calculated VAT: {vat:.2f}")
    st.write(f"Total Amount: {total:.2f}")

    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        add_transaction(customer_supplier, transaction_type,
                        description, price, vat, total, str(date), category)
        st.success(f"{transaction_type.capitalize()} added successfully!")

income, expense, balance = calculate_balance()
st.metric("Total Income", f"${income:.2f}")
st.metric("Total Expense", f"${expense:.2f}")
st.metric("Current Balance", f"${balance:.2f}")

st.subheader("Transaction History")
transactions = get_transactions()
df = pd.DataFrame(transactions,
                  columns=["ID", "Customer/Supplier", "Type", "Description", "Price", "VAT", "Total", "Date",
                           "Category"])
st.dataframe(df)

st.subheader("Income vs Expense Chart")
plot_transactions()
