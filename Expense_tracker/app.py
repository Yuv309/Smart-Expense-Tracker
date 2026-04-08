from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Ensure database exists
if not os.path.exists("expenses.db"):
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    if request.method == "POST":
        date = request.form["date"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        cur.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                    (date, amount, category, description))
        conn.commit()

    cur.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cur.fetchall()

    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0] or 0

    # Realistic budget alerts
    budget_limit = 30000
    budget_message = None
    if total > budget_limit:
        budget_message = f"⚠️ You've spent ₹{total}, which exceeds your budget limit of ₹{budget_limit}."

    # Category-specific warning
    category_alert = None
    for expense in expenses:
        if expense[3] == "Food" and expense[2] > 7000:
            category_alert = "🍽️ High spending on Food category. Consider reviewing your eating-out habits."
            break

    conn.close()
    return render_template("index.html", expenses=expenses, total=total,
                           budget_message=budget_message, category_alert=category_alert)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)


