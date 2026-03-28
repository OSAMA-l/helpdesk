# HelpDesk

**IT Support Ticketing System**

> **Note:** This is a re-upload. Cleaned up and pushed again.

A simple web-based help desk app I built for managing IT support tickets. Users can submit tickets, IT staff can track them, update statuses, add responses, and filter by priority or status. Everything runs locally with no external database needed — just Python and Flask.

Built this to learn Flask and to have something practical to show for IT support workflows.

---

## What It Does

- **Submit tickets** with name, email, department, category, priority, and description
- **Dashboard** showing ticket stats at a glance (open, in progress, resolved)
- **Filter & search** tickets by status, priority, or keyword
- **Ticket detail view** with full conversation history
- **Update status** (Open → In Progress → Resolved → Closed)
- **Update priority** (Low / Medium / High / Critical)
- **Add responses** to tickets — like an internal chat thread
- **Auto-generated ticket IDs** (HD-0001, HD-0002, etc.)
- **SQLite database** — no setup, no server, it just works

---

## Prerequisites

- **Python 3.8+** — Download from [python.org](https://www.python.org/downloads/)
- **Git** (optional) — Download from [git-scm.com](https://git-scm.com/downloads)

## Getting Started

**Option 1: Clone with Git**

```bash
git clone https://github.com/osama-l/helpdesk.git
cd helpdesk
```

**Option 2: Download ZIP**

1. Click the green **Code** button above → **Download ZIP**
2. Extract it and open a terminal in the folder

**Then install Flask and run it:**

```bash
pip install -r requirements.txt
python app.py
```

Open your browser and go to **http://127.0.0.1:5000** — that's it, you're in.

---

## Screenshots

### Dashboard
The main page shows ticket counts by status and priority, plus a list of recent tickets.

### Submit a Ticket
A clean form where users pick their department, category, priority, and describe the issue.

### Ticket Detail
View the full ticket with conversation history, status/priority controls, and a response form.

---

## Project Structure

```
helpdesk/
├── app.py              # Main Flask app — all the routes and logic
├── requirements.txt    # Just Flask
├── helpdesk.db         # SQLite database (auto-created on first run)
├── templates/          # HTML templates
│   ├── base.html       # Layout template (navbar, footer)
│   ├── dashboard.html  # Main dashboard
│   ├── tickets.html    # All tickets list with filters
│   ├── new_ticket.html # Ticket submission form
│   └── view_ticket.html # Single ticket detail view
├── static/
│   └── style.css       # All the styling
├── README.md
├── LICENSE
└── .gitignore
```

---

## How It Works (for the curious)

The app uses **Flask** (a Python web framework) to handle HTTP requests and render HTML pages. Data is stored in **SQLite**, which is just a single file (`helpdesk.db`) that gets created automatically when you first run the app. No database server to install or configure.

When someone submits a ticket, it gets saved to the database with a unique ID. IT staff can then view it, change its status, adjust priority, and add responses — all through the browser.

Key concepts used:
- **Routes** — URL paths mapped to Python functions (e.g., `/tickets/new` → `new_ticket()`)
- **Templates** — HTML files with dynamic data using Jinja2 (Flask's template engine)
- **SQLite** — Lightweight database stored as a single file
- **Forms** — HTML forms that send data to the server via POST requests

---

## Possible Improvements

Things I might add later:
- User login and authentication
- Email notifications when a ticket is updated
- File attachment support
- Admin panel for managing users
- Export tickets to CSV

---

## Built With

- **Python 3** + **Flask** — Web framework
- **SQLite** — Database (built into Python, no install needed)
- **Jinja2** — HTML templating (comes with Flask)
- **CSS** — Custom styling, no frameworks

---

## License

MIT — do whatever you want with it.

---

## Author

**Osama Al-Shahri**
- Portfolio: [osama-l.github.io](https://osama-l.github.io)
- Email: o.alshahri@outlook.com
