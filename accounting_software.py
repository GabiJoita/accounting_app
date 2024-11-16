import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import customtkinter as cst
from customtkinter import *

# Database setup
def setup_db():
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


def calculate_vat_and_total(price, vat_rate):
    '''function which create a formula
       to sum vat and and price    
    '''
    vat = price * vat_rate
    total = price + vat
    return vat, total

def calculate_and_display_total():
    '''display with this function
       vat and total
    '''
    try:
        price = float(price_entry.get())
        vat_rate = float(vat_rate_var.get()) / 100  

        vat, total = calculate_vat_and_total(price, vat_rate)

        vat_entry_var.set(f"{vat:.2f}")
        total_entry_var.set(f"{total:.2f}")

    except ValueError:
        messagebox.showerror("Input Error", "Invalid price or VAT rate. Please enter valid numbers.")


def add_transaction():
    customer_supplier = customer_supplier_entry.get()
    transaction_type = type_var.get()
    description = description_entry.get()
    price = price_entry.get()
    vat = vat_entry_var.get()  
    date = date_entry.get()
    category = category_entry.get()

    if not price or not date:
        messagebox.showerror("Input Error", "Price and Date are required!")
        return

    try:
        price = float(price)
        vat = float(vat) 
        total = price + vat 
    except ValueError:
        messagebox.showerror("Input Error", "Invalid price or VAT. Please enter valid numbers.")
        return

    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO transactions (customer_supplier, type, description, price, vat, total, date, category)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (customer_supplier, transaction_type, description, price, vat, total, date, category))
    conn.commit()
    conn.close()

    # Clear input fields
    customer_supplier_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    vat_entry_var.set("")
    total_entry_var.set("")
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    messagebox.showinfo("Success", f"{transaction_type.capitalize()} added successfully!")
    update_balance()
    view_transactions()

# Function to update the balance
def update_balance():
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM transactions WHERE type='income'")
    income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(total) FROM transactions WHERE type='expense'")
    expense = cursor.fetchone()[0] or 0
    balance = income - expense
    balance_label.config(text=f"Current Balance: ${balance:.2f}")
    conn.close()

# Function to view transactions
def view_transactions():
    for row in transactions_tree.get_children():
        transactions_tree.delete(row)

    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    for row in rows:
        transactions_tree.insert("", tk.END, values=row)
    conn.close()

# GUI setup
root = tk.Tk()
root.title("Accounting Program")

# Set the background color of the main window
root.configure(bg="#204bb9")  # Light grey background

# Define button styles
button_style = {"bg": "#46c2dd", "fg": "white", "activebackground": "#388e3c", "activeforeground": "white"}

# Define label and entry colors
label_style = {"bg": "#f0f0f0", "fg": "#333"}
entry_bg_color = "#204bb9"

# Customer/Supplier Entry
tk.Label(root, text="Customer/Supplier:", bg=entry_bg_color, fg='white').grid(row=0, column=0, padx=10, pady=5)
customer_supplier_entry = tk.Entry(root)
customer_supplier_entry.grid(row=0, column=1, padx=10, pady=5)

# Type (Income/Expense)
tk.Label(root, text="Type:", bg=entry_bg_color, fg='white').grid(row=1, column=0, padx=10, pady=5)
type_var = tk.StringVar(value="income")
type_option = ttk.Combobox(root, textvariable=type_var, values=["income", "expense"])
type_option.grid(row=1, column=1, padx=10, pady=5)

# Description Entry
tk.Label(root, text="Description:", bg=entry_bg_color, fg='white').grid(row=2, column=0, padx=10, pady=5)
description_entry = tk.Entry(root)
description_entry.grid(row=2, column=1, padx=10, pady=5)

# Price Entry
tk.Label(root, text="Price:", bg=entry_bg_color, fg='white').grid(row=3, column=0, padx=10, pady=5)
price_entry = tk.Entry(root)
price_entry.grid(row=3, column=1, padx=10, pady=5)

# VAT Rate Selection (19%, 9%, 0%)
tk.Label(root, text="Select VAT Rate:", bg=entry_bg_color, fg='white').grid(row=4, column=0, padx=10, pady=5)
vat_rate_var = tk.StringVar(value="19")  # Default VAT is 19%
vat_rate_option = ttk.Combobox(root, textvariable=vat_rate_var, values=["19", "9", "0"])
vat_rate_option.grid(row=4, column=1, padx=10, pady=5)

# VAT and Total Calculation Button
calculate_button = cst.CTkButton(root, text="Calculate VAT and Total", command=calculate_and_display_total)
calculate_button.grid(row=3, column=2, padx=10, pady=5)

# VAT Entry (Read-Only)
tk.Label(root, text="Calculated VAT:", bg=entry_bg_color, fg='white').grid(row=5, column=0, padx=10, pady=5)
vat_entry_var = tk.StringVar()
vat_entry = tk.Entry(root, textvariable=vat_entry_var, state="readonly")
vat_entry.grid(row=5, column=1, padx=10, pady=5)

# Total Entry (Read-Only)
tk.Label(root, text="Calculated Total:", bg=entry_bg_color, fg='white').grid(row=6, column=0, padx=10, pady=5)
total_entry_var = tk.StringVar()
total_entry = tk.Entry(root, textvariable=total_entry_var, state="readonly")
total_entry.grid(row=6, column=1, padx=10, pady=5)

# Date Entry
tk.Label(root, text="Date (YYYY-MM-DD):", bg=entry_bg_color, fg='white').grid(row=7, column=0, padx=10, pady=5)
date_entry = tk.Entry(root)
date_entry.grid(row=7, column=1, padx=10, pady=5)

# Category Entry
tk.Label(root, text="Category:", bg=entry_bg_color, fg='white').grid(row=8, column=0, padx=10, pady=5)
category_entry = tk.Entry(root)
category_entry.grid(row=8, column=1, padx=10, pady=5)

# Add Transaction Button
add_button = cst.CTkButton(root, text="Add Transaction", command=add_transaction)
add_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

# Balance Label
balance_label = tk.Label(root, text="Current Balance: $0.00", bg=entry_bg_color, fg='white', font=("Arial", 14))
balance_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

# Transactions History Table
columns = ("ID", "Customer/Supplier", "Type", "Description", "Price", "VAT", "Total", "Date", "Category")
transactions_tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    transactions_tree.heading(col, text=col)
    transactions_tree.column(col, width=120)
transactions_tree.grid(row=11, column=0, columnspan=3, padx=10, pady=10)

# Initialize database and update balance
setup_db()
update_balance()
view_transactions()

root.mainloop()