"""
database.py - SQLite Database Management for PlantPal
=====================================================
This module manages database connections, table creation, seed data,
and all CRUD (Create, Read, Update, Delete) operations for:
- Plants
- Watering logs & schedules
- Care tasks
- Daily gardening challenges

Written cleanly for first-year IT engineering students to learn
practical SQLite database operations using Python.
"""

import os
import sqlite3
from datetime import datetime, timedelta, date

# Path to the database file inside the 'instance' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'plantpal.db')


def get_db():
    """
    Establish and return a connection to the SQLite database.
    row_factory is set to sqlite3.Row so columns can be accessed by name.
    """
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initialize database tables if they do not already exist,
    and seed the default gardening challenges.
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1. Plants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            location TEXT,
            sunlight TEXT NOT NULL,
            watering_interval_days INTEGER NOT NULL DEFAULT 7,
            last_watered_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Watering history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watering_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            watered_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE
        );
    """)

    # 3. Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            plant_id INTEGER,
            task_type TEXT NOT NULL DEFAULT 'other',
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE SET NULL
        );
    """)

    # 4. Challenges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            completed_date TEXT
        );
    """)

    # Seed default daily challenges if not already present
    default_challenges = [
        (
            "soil_check",
            "Check soil moisture",
            "Insert your finger 1–2 inches into your plant's soil before watering. If it feels dry, it's time to hydrate!",
            "Care Habit"
        ),
        (
            "leaf_inspect",
            "Observe your plant's leaves",
            "Check the top and underside of leaves for dust, discoloration, or tiny pests. Wipe gently if dusty.",
            "Observation"
        ),
        (
            "learn_fact",
            "Learn one new plant care fact",
            "Explore the Plant Library to discover native climates, light needs, or propagation methods.",
            "Learning"
        ),
        (
            "outdoor_time",
            "Spend 10 minutes with plants",
            "Step outdoors, visit a balcony, or care for indoor plants to relax and reconnect with nature.",
            "Mindfulness"
        ),
        (
            "herb_garden",
            "Start or propagate a plant",
            "Take a stem cutting from a pothos, mint, or money plant and place it in clean water to root.",
            "Propagation"
        )
    ]

    for key, title, desc, cat in default_challenges:
        cursor.execute("""
            INSERT OR IGNORE INTO challenges (challenge_key, title, description, category, completed)
            VALUES (?, ?, ?, ?, 0)
        """, (key, title, desc, cat))

    conn.commit()
    conn.close()


# -------------------------------------------------------------
# HELPER: WATERING CALCULATIONS
# -------------------------------------------------------------
def calculate_watering_info(last_watered_date_str, interval_days):
    """
    Computes next watering date, days remaining, and status category.
    Returns a dict with:
    - next_watering_date: 'YYYY-MM-DD'
    - days_diff: integer (-1 = 1 day overdue, 0 = due today, +2 = in 2 days)
    - status: 'overdue' | 'due-today' | 'upcoming'
    - status_label: human readable badge text
    """
    try:
        last_date = datetime.strptime(last_watered_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        last_date = date.today()

    next_date = last_date + timedelta(days=interval_days)
    today = date.today()
    days_diff = (next_date - today).days

    if days_diff < 0:
        overdue_days = abs(days_diff)
        status = "overdue"
        status_label = f"Overdue by {overdue_days} day{'s' if overdue_days > 1 else ''}"
    elif days_diff == 0:
        status = "due-today"
        status_label = "Due Today"
    else:
        status = "upcoming"
        status_label = f"Due in {days_diff} day{'s' if days_diff > 1 else ''}"

    return {
        "next_watering_date": next_date.strftime("%Y-%m-%d"),
        "days_diff": days_diff,
        "status": status,
        "status_label": status_label
    }


# -------------------------------------------------------------
# PLANT CRUD OPERATIONS
# -------------------------------------------------------------
def get_all_plants(search_query=None, sunlight_filter=None):
    """
    Fetch all plants with optional search and sunlight filtering.
    Augments each plant record with calculated watering schedule info.
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM plants WHERE 1=1"
    params = []

    if search_query:
        sql += " AND (name LIKE ? OR species LIKE ? OR location LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term])

    if sunlight_filter and sunlight_filter != "all":
        sql += " AND sunlight = ?"
        params.append(sunlight_filter)

    sql += " ORDER BY name COLLATE NOCASE ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    plants = []
    for row in rows:
        p = dict(row)
        watering_info = calculate_watering_info(p["last_watered_date"], p["watering_interval_days"])
        p.update(watering_info)
        plants.append(p)

    return plants


def get_plant(plant_id):
    """
    Fetch a single plant by ID and attach watering schedule info.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    p = dict(row)
    watering_info = calculate_watering_info(p["last_watered_date"], p["watering_interval_days"])
    p.update(watering_info)
    return p


def create_plant(name, species, location, sunlight, watering_interval_days, last_watered_date, notes):
    """
    Insert a new plant record and log the initial watering entry.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO plants (name, species, location, sunlight, watering_interval_days, last_watered_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, species, location, sunlight, int(watering_interval_days), last_watered_date, notes))

    new_id = cursor.lastrowid

    # Automatically add initial watering history entry
    cursor.execute("""
        INSERT INTO watering_history (plant_id, watered_date, notes)
        VALUES (?, ?, 'Initial watering log when added to PlantPal')
    """, (new_id, last_watered_date))

    conn.commit()
    conn.close()
    return new_id


def update_plant(plant_id, name, species, location, sunlight, watering_interval_days, last_watered_date, notes):
    """
    Update an existing plant's details.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plants
        SET name = ?, species = ?, location = ?, sunlight = ?,
            watering_interval_days = ?, last_watered_date = ?, notes = ?
        WHERE id = ?
    """, (name, species, location, sunlight, int(watering_interval_days), last_watered_date, notes, plant_id))

    conn.commit()
    conn.close()


def delete_plant(plant_id):
    """
    Delete a plant and its cascade relationships.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()


# -------------------------------------------------------------
# WATERING OPERATIONS & HISTORY
# -------------------------------------------------------------
def log_watering(plant_id, watered_date=None, notes=None):
    """
    Record a watering event in watering_history and update last_watered_date on the plant.
    """
    if not watered_date:
        watered_date = date.today().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    # Insert watering history entry
    cursor.execute("""
        INSERT INTO watering_history (plant_id, watered_date, notes)
        VALUES (?, ?, ?)
    """, (plant_id, watered_date, notes or "Marked as watered"))

    # Update plant's last_watered_date
    cursor.execute("""
        UPDATE plants
        SET last_watered_date = ?
        WHERE id = ?
    """, (watered_date, plant_id))

    conn.commit()
    conn.close()


def get_watering_history(plant_id):
    """
    Fetch all historical watering logs for a specific plant, newest first.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM watering_history
        WHERE plant_id = ?
        ORDER BY watered_date DESC, id DESC
    """, (plant_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_scheduler_data():
    """
    Retrieve all plants categorized into:
    - overdue
    - due_today
    - upcoming
    Sorted by urgency (most overdue first).
    """
    plants = get_all_plants()
    overdue = []
    due_today = []
    upcoming = []

    for p in plants:
        if p["status"] == "overdue":
            overdue.append(p)
        elif p["status"] == "due-today":
            due_today.append(p)
        else:
            upcoming.append(p)

    # Sort overdue by most overdue (lowest days_diff)
    overdue.sort(key=lambda x: x["days_diff"])
    # Sort upcoming by closest due date
    upcoming.sort(key=lambda x: x["days_diff"])

    return {
        "overdue": overdue,
        "due_today": due_today,
        "upcoming": upcoming,
        "total_count": len(plants)
    }


# -------------------------------------------------------------
# CARE TASKS CRUD
# -------------------------------------------------------------
def get_tasks(filter_status=None):
    """
    Retrieve care tasks with optional filtering ('pending', 'completed', or None for all).
    Joins with plants table to include plant name if associated.
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = """
        SELECT tasks.*, plants.name AS plant_name, plants.species AS plant_species
        FROM tasks
        LEFT JOIN plants ON tasks.plant_id = plants.id
        WHERE 1=1
    """
    params = []

    if filter_status in ("pending", "completed"):
        sql += " AND tasks.status = ?"
        params.append(filter_status)

    sql += " ORDER BY tasks.status DESC, tasks.due_date ASC, tasks.id DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    today_str = date.today().strftime("%Y-%m-%d")
    for r in rows:
        t = dict(r)
        t["is_overdue"] = (t["status"] == "pending" and t["due_date"] < today_str)
        t["is_today"] = (t["status"] == "pending" and t["due_date"] == today_str)
        tasks.append(t)

    return tasks


def create_task(title, plant_id, task_type, due_date):
    """
    Create a new care task.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, plant_id, task_type, due_date, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (title, plant_id if plant_id else None, task_type or 'other', due_date))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def toggle_task(task_id):
    """
    Toggle task status between 'pending' and 'completed'.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row:
        current_status = row["status"]
        if current_status == "pending":
            new_status = "completed"
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_status = "pending"
            completed_at = None

        cursor.execute("""
            UPDATE tasks
            SET status = ?, completed_at = ?
            WHERE id = ?
        """, (new_status, completed_at, task_id))
        conn.commit()

    conn.close()


def delete_task(task_id):
    """
    Delete a care task.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


# -------------------------------------------------------------
# DAILY GARDENING CHALLENGES
# -------------------------------------------------------------
def get_challenges():
    """
    Fetch all challenges and calculate progress statistics.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM challenges ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    challenges = [dict(r) for r in rows]
    total = len(challenges)
    completed_count = sum(1 for c in challenges if c["completed"] == 1)
    progress_percent = int((completed_count / total * 100)) if total > 0 else 0

    return {
        "items": challenges,
        "total": total,
        "completed_count": completed_count,
        "progress_percent": progress_percent
    }


def toggle_challenge(challenge_key):
    """
    Toggle a challenge between completed (1) and incomplete (0).
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM challenges WHERE challenge_key = ?", (challenge_key,))
    row = cursor.fetchone()

    if row:
        new_state = 0 if row["completed"] == 1 else 1
        comp_date = date.today().strftime("%Y-%m-%d") if new_state == 1 else None
        cursor.execute("""
            UPDATE challenges
            SET completed = ?, completed_date = ?
            WHERE challenge_key = ?
        """, (new_state, comp_date, challenge_key))
        conn.commit()

    conn.close()


# -------------------------------------------------------------
# DASHBOARD OVERVIEW & STATS
# -------------------------------------------------------------
def get_dashboard_stats():
    """
    Calculates summary statistics from actual database records:
    - Total plants
    - Plants due for watering (overdue + due today)
    - Pending care tasks
    - Completed tasks
    - Upcoming watering reminders list (top 4 next due)
    """
    conn = get_db()
    cursor = conn.cursor()

    # Plant count
    cursor.execute("SELECT COUNT(*) AS total FROM plants")
    total_plants = cursor.fetchone()["total"]

    # Pending and completed tasks
    cursor.execute("SELECT COUNT(*) AS pending FROM tasks WHERE status = 'pending'")
    pending_tasks = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE status = 'completed'")
    completed_tasks = cursor.fetchone()["completed"]

    conn.close()

    # Calculate watering metrics from all plants
    plants = get_all_plants()
    due_for_watering = sum(1 for p in plants if p["status"] in ("overdue", "due-today"))

    # Sort plants by urgency for the reminder section
    sorted_reminders = sorted(plants, key=lambda p: p["days_diff"])[:5]

    return {
        "total_plants": total_plants,
        "due_for_watering": due_for_watering,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "reminders": sorted_reminders
    }
