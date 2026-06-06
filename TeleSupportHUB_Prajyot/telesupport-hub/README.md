# TeleSupport Hub — Prajyot's Project

A Flask-based telecom customer support portal with SQLite (default) and MySQL support.

---

## 👤 Login Credentials

### Customer Login
| Field    | Value                    |
|----------|--------------------------|
| Email    | prajyot2017@gmail.com    |
| Password | pass123                  |

### Agent Login
| Field    | Value                    |
|----------|--------------------------|
| Email    | agent@telesupport.com    |
| Password | agent123                 |

---

## 🚀 How to Run the Project

### Step 1 — Install Python
Make sure Python 3.10 or above is installed.
Download from: https://www.python.org/downloads/

### Step 2 — Open Terminal / Command Prompt
Navigate to the project folder:
```
cd telesupport-hub
```

### Step 3 — Install Dependencies
```
pip install -r requirements.txt
```

### Step 4 — Run the App
```
python app.py
```

### Step 5 — Open in Browser
Go to: **http://localhost:5000**

---

## 📁 Project Structure

```
telesupport-hub/
├── app.py                  ← Main Flask application
├── schema.sql              ← MySQL schema (for MySQL setup)
├── requirements.txt        ← Python dependencies
├── telesupport_hub.db      ← SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css       ← Stylesheet
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── services.html
    ├── raise_ticket.html
    ├── agent_login.html
    ├── agent_dashboard.html
    └── database_preview.html
```

---

## 🗄️ Database Info

The project uses **SQLite by default** — no setup needed.
The database file `telesupport_hub.db` is already included with data.

### Tables:
- `customers` — stores registered users (Prajyot is pre-loaded)
- `agents` — support agent accounts
- `purchases` — services bought by customers
- `tickets` — support tickets raised by customers

### To use MySQL instead:
1. Create a `.env` file in the `telesupport-hub/` folder:
```
DB_TYPE=mysql
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=telesupport_hub
```
2. Run the schema: `mysql -u root -p < schema.sql`
3. Then run: `python app.py`

---

## 🌐 Pages

| URL               | Page                        |
|-------------------|-----------------------------|
| /                 | Home                        |
| /register         | Customer Registration       |
| /login            | Customer Login              |
| /dashboard        | Customer Dashboard          |
| /services         | Buy a Service               |
| /raise-ticket     | Raise a Support Ticket      |
| /agent            | Agent Login                 |
| /agent-dashboard  | Agent Dashboard             |
| /database-preview | View Database Records       |
| /logout           | Logout                      |
