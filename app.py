# app.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Debugging: Check if tables exist
def check_tables_exist():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    conn.close()
    return tables

print("Tables in database:", check_tables_exist())

# Database connection
def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# Page title
st.title("Personal Finance Tracker")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "Set Budget", "Set Savings Goal"])

# Dashboard Page
if page == "Dashboard":
    st.header("Dashboard")

    # Fetch data from the database
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    budget = conn.execute('SELECT * FROM budget ORDER BY id DESC LIMIT 1').fetchone()
    savings = conn.execute('SELECT * FROM savings ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    # Display budget and savings
    if budget:
        st.subheader(f"Budget: ₹{budget['amount']:,.2f}")  # Updated to ₹
    if savings:
        progress = (savings['current'] / savings['goal']) * 100
        st.subheader(f"Savings Progress: {progress:.2f}%")

    # Display expenses in a table
    if expenses:
        st.subheader("Expenses")
        expenses_df = pd.DataFrame(expenses, columns=["ID", "Amount", "Category", "Description"])
        st.dataframe(expenses_df)

        # Visualize expenses by category
        st.subheader("Spending by Category")
        category_totals = expenses_df.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(category_totals, values="Amount", names="Category", title="Expense Distribution")
        st.plotly_chart(fig)

# Add Expense Page
elif page == "Add Expense":
    st.header("Add Expense")

    # Input fields for expense
    amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)  # Updated to ₹
    category = st.text_input("Category")
    description = st.text_input("Description")

    if st.button("Add Expense"):
        if amount and category:
            conn = get_db_connection()
            conn.execute('INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)',
                         (amount, category, description))
            conn.commit()
            conn.close()
            st.success("Expense added successfully!")
        else:
            st.error("Please fill in all fields.")

# Set Budget Page
elif page == "Set Budget":
    st.header("Set Budget")

    # Input field for budget
    budget_amount = st.number_input("Monthly Budget (₹)", min_value=0.0, step=0.01)  # Updated to ₹

    if st.button("Set Budget"):
        if budget_amount:
            conn = get_db_connection()
            conn.execute('INSERT INTO budget (amount) VALUES (?)', (budget_amount,))
            conn.commit()
            conn.close()
            st.success("Budget set successfully!")
        else:
            st.error("Please enter a valid budget.")

# Set Savings Goal Page
elif page == "Set Savings Goal":
    st.header("Set Savings Goal")

    # Input fields for savings goal
    savings_goal = st.number_input("Savings Goal (₹)", min_value=0.0, step=0.01)  # Updated to ₹
    current_savings = st.number_input("Current Savings (₹)", min_value=0.0, step=0.01)  # Updated to ₹

    if st.button("Set Savings Goal"):
        if savings_goal and current_savings:
            conn = get_db_connection()
            conn.execute('INSERT INTO savings (goal, current) VALUES (?, ?)',
                         (savings_goal, current_savings))
            conn.commit()
            conn.close()
            st.success("Savings goal updated successfully!")
        else:
            st.error("Please fill in all fields.")