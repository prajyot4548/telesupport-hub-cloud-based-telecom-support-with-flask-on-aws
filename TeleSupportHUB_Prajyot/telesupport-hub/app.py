import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for

try:
    import mysql.connector
except ImportError:
    mysql = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "telesupport-dev-secret")

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
SQLITE_PATH = os.path.join(app.root_path, "telesupport_hub.db")


@contextmanager
def get_db():
    if DB_TYPE == "mysql":
        if mysql is None:
            raise RuntimeError("mysql-connector-python is required when DB_TYPE=mysql")
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "telesupport_hub"),
        )
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def execute(conn, query, params=()):
    cursor = conn.cursor(dictionary=True) if DB_TYPE == "mysql" else conn.cursor()
    cursor.execute(query, params)
    return cursor


def rows(cursor):
    return cursor.fetchall()


def one(cursor):
    return cursor.fetchone()


def init_db():
    with get_db() as conn:
        if DB_TYPE == "mysql":
            statements = [
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    mobile VARCHAR(20) NOT NULL,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password VARCHAR(120) NOT NULL,
                    address VARCHAR(255) NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS agents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password VARCHAR(120) NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS purchases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT NOT NULL,
                    description TEXT NOT NULL,
                    plan_type VARCHAR(50) NOT NULL,
                    priority VARCHAR(20) NOT NULL,
                    status VARCHAR(30) DEFAULT 'Open',
                    date_raised TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """,
            ]
        else:
            statements = [
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    mobile TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    address TEXT NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    service_name TEXT NOT NULL,
                    purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT DEFAULT 'Open',
                    date_raised TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """,
            ]

        for statement in statements:
            execute(conn, statement)

        # Default agent
        execute(
            conn,
            "INSERT OR IGNORE INTO agents (id, name, email, password) VALUES (?, ?, ?, ?)"
            if DB_TYPE != "mysql"
            else "INSERT IGNORE INTO agents (id, name, email, password) VALUES (%s, %s, %s, %s)",
            (1, "Support Agent", "agent@telesupport.com", "agent123"),
        )
        # Default customer - Prajyot
        execute(
            conn,
            "INSERT OR IGNORE INTO customers (id, name, mobile, email, password, address) VALUES (?, ?, ?, ?, ?, ?)"
            if DB_TYPE != "mysql"
            else "INSERT IGNORE INTO customers (id, name, mobile, email, password, address) VALUES (%s, %s, %s, %s, %s, %s)",
            (1, "Prajyot", "9876543210", "prajyot2017@gmail.com", "pass123", "Pune, Maharashtra"),
        )


def login_required():
    return "customer_id" in session


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = (
            request.form["name"],
            request.form["mobile"],
            request.form["email"].lower(),
            request.form["password"],
            request.form["address"],
        )
        try:
            with get_db() as conn:
                execute(
                    conn,
                    "INSERT INTO customers (name, mobile, email, password, address) VALUES (?, ?, ?, ?, ?)"
                    if DB_TYPE != "mysql"
                    else "INSERT INTO customers (name, mobile, email, password, address) VALUES (%s, %s, %s, %s, %s)",
                    data,
                )
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("Email already exists or database error occurred.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        with get_db() as conn:
            customer = one(
                execute(
                    conn,
                    "SELECT * FROM customers WHERE email = ? AND password = ?"
                    if DB_TYPE != "mysql"
                    else "SELECT * FROM customers WHERE email = %s AND password = %s",
                    (email, password),
                )
            )
        if customer:
            session.clear()
            session["customer_id"] = customer["id"]
            session["customer_name"] = customer["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid customer email or password.", "error")
    return render_template("login.html")


@app.route("/agent", methods=["GET", "POST"])
def agent_login():
    if request.method == "POST":
        with get_db() as conn:
            agent = one(
                execute(
                    conn,
                    "SELECT * FROM agents WHERE email = ? AND password = ?"
                    if DB_TYPE != "mysql"
                    else "SELECT * FROM agents WHERE email = %s AND password = %s",
                    (request.form["email"].lower(), request.form["password"]),
                )
            )
        if agent:
            session.clear()
            session["agent_id"] = agent["id"]
            session["agent_name"] = agent["name"]
            return redirect(url_for("agent_dashboard"))
        flash("Invalid agent credentials.", "error")
    return render_template("agent_login.html")


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    customer_id = session["customer_id"]
    with get_db() as conn:
        purchases = rows(
            execute(
                conn,
                "SELECT * FROM purchases WHERE customer_id = ? ORDER BY id DESC"
                if DB_TYPE != "mysql"
                else "SELECT * FROM purchases WHERE customer_id = %s ORDER BY id DESC",
                (customer_id,),
            )
        )
        tickets = rows(
            execute(
                conn,
                "SELECT * FROM tickets WHERE customer_id = ? ORDER BY id DESC"
                if DB_TYPE != "mysql"
                else "SELECT * FROM tickets WHERE customer_id = %s ORDER BY id DESC",
                (customer_id,),
            )
        )
    return render_template("dashboard.html", purchases=purchases, tickets=tickets)


@app.route("/services", methods=["GET", "POST"])
def services():
    if not login_required():
        return redirect(url_for("login"))
    plans = [
        ("Fiber Broadband 100 Mbps", "High-speed unlimited home internet."),
        ("5G Mobile Data Pack", "Daily data plan for mobile customers."),
        ("Business Voice Support", "Priority voice support for small business."),
        ("OTT Combo Plan", "Internet plan bundled with entertainment services."),
    ]
    if request.method == "POST":
        with get_db() as conn:
            execute(
                conn,
                "INSERT INTO purchases (customer_id, service_name) VALUES (?, ?)"
                if DB_TYPE != "mysql"
                else "INSERT INTO purchases (customer_id, service_name) VALUES (%s, %s)",
                (session["customer_id"], request.form["service_name"]),
            )
        flash("Service purchased successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("services.html", plans=plans)


@app.route("/raise-ticket", methods=["GET", "POST"])
def raise_ticket():
    if not login_required():
        return redirect(url_for("login"))
    if request.method == "POST":
        with get_db() as conn:
            execute(
                conn,
                "INSERT INTO tickets (customer_id, description, plan_type, priority, status, date_raised) VALUES (?, ?, ?, ?, ?, ?)"
                if DB_TYPE != "mysql"
                else "INSERT INTO tickets (customer_id, description, plan_type, priority, status, date_raised) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    session["customer_id"],
                    request.form["description"],
                    request.form["plan_type"],
                    request.form["priority"],
                    "Open",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        flash("Support ticket raised successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("raise_ticket.html")


@app.route("/agent-dashboard")
def agent_dashboard():
    if "agent_id" not in session:
        return redirect(url_for("agent_login"))
    with get_db() as conn:
        tickets = rows(
            execute(
                conn,
                """
                SELECT tickets.*, customers.name, customers.email, customers.mobile
                FROM tickets JOIN customers ON tickets.customer_id = customers.id
                ORDER BY tickets.id DESC
                """
            )
        )
    return render_template("agent_dashboard.html", tickets=tickets)


@app.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def update_ticket(ticket_id):
    if "agent_id" not in session:
        return redirect(url_for("agent_login"))
    with get_db() as conn:
        execute(
            conn,
            "UPDATE tickets SET status = ? WHERE id = ?"
            if DB_TYPE != "mysql"
            else "UPDATE tickets SET status = %s WHERE id = %s",
            (request.form["status"], ticket_id),
        )
    flash("Ticket status updated.", "success")
    return redirect(url_for("agent_dashboard"))


@app.route("/database-preview")
def database_preview():
    with get_db() as conn:
        customers = rows(execute(conn, "SELECT id, name, mobile, email, address FROM customers"))
        purchases = rows(execute(conn, "SELECT * FROM purchases ORDER BY id DESC"))
        tickets = rows(execute(conn, "SELECT * FROM tickets ORDER BY id DESC"))
    return render_template("database_preview.html", customers=customers, purchases=purchases, tickets=tickets)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
