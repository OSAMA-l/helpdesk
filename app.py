"""
HelpDesk - IT Support Ticketing System
=======================================
A lightweight web-based help desk application for managing
IT support requests, built with Flask and SQLite.

Author: Osama Al-Shahri
GitHub: https://github.com/osama-l/helpdesk
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g

# ──────────────────────────────────────────────
# App Configuration
# ──────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpdesk.db")


# ──────────────────────────────────────────────
# Database Setup
# ──────────────────────────────────────────────

def get_db():
    """Get a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Access columns by name
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close database connection when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create database tables if they don't exist."""
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT DEFAULT 'General',
            category TEXT DEFAULT 'General',
            priority TEXT DEFAULT 'Medium',
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
        )
    """)
    db.commit()
    db.close()


def generate_ticket_id():
    """Generate a unique ticket ID like HD-0001."""
    db = get_db()
    row = db.execute("SELECT MAX(id) FROM tickets").fetchone()
    next_id = (row[0] or 0) + 1
    return f"HD-{next_id:04d}"


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Main dashboard with ticket statistics."""
    db = get_db()

    # Get counts by status
    stats = {}
    for status in ["Open", "In Progress", "Resolved", "Closed"]:
        row = db.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = ?", (status,)
        ).fetchone()
        stats[status] = row[0]

    stats["Total"] = sum(stats.values())

    # Get counts by priority
    priority_stats = {}
    for priority in ["Low", "Medium", "High", "Critical"]:
        row = db.execute(
            "SELECT COUNT(*) FROM tickets WHERE priority = ? AND status != 'Closed'",
            (priority,),
        ).fetchone()
        priority_stats[priority] = row[0]

    # Recent tickets (last 10)
    recent = db.execute(
        "SELECT * FROM tickets ORDER BY created_at DESC LIMIT 10"
    ).fetchall()

    return render_template(
        "dashboard.html", stats=stats, priority_stats=priority_stats, recent=recent
    )


@app.route("/tickets")
def tickets():
    """View all tickets with optional filtering."""
    db = get_db()

    # Get filter parameters
    status_filter = request.args.get("status", "all")
    priority_filter = request.args.get("priority", "all")
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)

    if priority_filter != "all":
        query += " AND priority = ?"
        params.append(priority_filter)

    if search:
        query += " AND (subject LIKE ? OR ticket_id LIKE ? OR name LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])

    query += " ORDER BY created_at DESC"
    all_tickets = db.execute(query, params).fetchall()

    return render_template(
        "tickets.html",
        tickets=all_tickets,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search=search,
    )


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    """Create a new support ticket."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "General")
        category = request.form.get("category", "General")
        priority = request.form.get("priority", "Medium")
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()

        # Validation
        if not all([name, email, subject, description]):
            flash("Please fill in all required fields.", "error")
            return render_template("new_ticket.html")

        db = get_db()
        ticket_id = generate_ticket_id()

        db.execute(
            """INSERT INTO tickets
               (ticket_id, name, email, department, category, priority, subject, description)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticket_id, name, email, department, category, priority, subject, description),
        )
        db.commit()

        flash(f"Ticket {ticket_id} created successfully!", "success")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    return render_template("new_ticket.html")


@app.route("/tickets/<ticket_id>")
def view_ticket(ticket_id):
    """View a single ticket with its response history."""
    db = get_db()

    ticket = db.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
    ).fetchone()

    if not ticket:
        flash("Ticket not found.", "error")
        return redirect(url_for("tickets"))

    responses = db.execute(
        "SELECT * FROM responses WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,),
    ).fetchall()

    return render_template("view_ticket.html", ticket=ticket, responses=responses)


@app.route("/tickets/<ticket_id>/respond", methods=["POST"])
def respond_ticket(ticket_id):
    """Add a response to a ticket."""
    author = request.form.get("author", "").strip()
    message = request.form.get("message", "").strip()

    if not all([author, message]):
        flash("Please fill in all fields.", "error")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    db = get_db()

    db.execute(
        "INSERT INTO responses (ticket_id, author, message) VALUES (?, ?, ?)",
        (ticket_id, author, message),
    )
    db.execute(
        "UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
        (ticket_id,),
    )
    db.commit()

    flash("Response added.", "success")
    return redirect(url_for("view_ticket", ticket_id=ticket_id))


@app.route("/tickets/<ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    """Update a ticket's status."""
    new_status = request.form.get("status")

    if new_status not in ["Open", "In Progress", "Resolved", "Closed"]:
        flash("Invalid status.", "error")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    db = get_db()
    db.execute(
        "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
        (new_status, ticket_id),
    )

    # Auto-add a status change note
    db.execute(
        "INSERT INTO responses (ticket_id, author, message) VALUES (?, ?, ?)",
        (ticket_id, "System", f"Status changed to {new_status}"),
    )
    db.commit()

    flash(f"Status updated to {new_status}.", "success")
    return redirect(url_for("view_ticket", ticket_id=ticket_id))


@app.route("/tickets/<ticket_id>/priority", methods=["POST"])
def update_priority(ticket_id):
    """Update a ticket's priority."""
    new_priority = request.form.get("priority")

    if new_priority not in ["Low", "Medium", "High", "Critical"]:
        flash("Invalid priority.", "error")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    db = get_db()
    db.execute(
        "UPDATE tickets SET priority = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
        (new_priority, ticket_id),
    )
    db.execute(
        "INSERT INTO responses (ticket_id, author, message) VALUES (?, ?, ?)",
        (ticket_id, "System", f"Priority changed to {new_priority}"),
    )
    db.commit()

    flash(f"Priority updated to {new_priority}.", "success")
    return redirect(url_for("view_ticket", ticket_id=ticket_id))


# ──────────────────────────────────────────────
# Template Filters
# ──────────────────────────────────────────────

@app.template_filter("timeago")
def timeago_filter(dt_string):
    """Convert a datetime string to a human-readable 'time ago' format."""
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago"
        else:
            return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return dt_string


@app.template_filter("status_color")
def status_color_filter(status):
    """Return a CSS color class for a ticket status."""
    colors = {
        "Open": "blue",
        "In Progress": "orange",
        "Resolved": "green",
        "Closed": "gray",
    }
    return colors.get(status, "gray")


@app.template_filter("priority_color")
def priority_color_filter(priority):
    """Return a CSS color class for a ticket priority."""
    colors = {
        "Low": "green",
        "Medium": "blue",
        "High": "orange",
        "Critical": "red",
    }
    return colors.get(priority, "gray")


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║   HelpDesk - IT Support Ticketing    ║")
    print("  ║   Running on http://127.0.0.1:5000   ║")
    print("  ╚══════════════════════════════════════╝\n")
    app.run(debug=True, port=5000)
