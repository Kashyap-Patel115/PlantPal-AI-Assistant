"""
app.py - PlantPal Main Flask Application
=========================================
A complete, beginner-friendly Flask web application for managing plants,
tracking watering schedules, organizing plant care tasks, exploring a plant library,
taking daily gardening challenges, and asking questions to a local SmolLM2 360M AI model.
"""

import os
from datetime import date, datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify
)

import database
import plant_library
import ai_service

app = Flask(__name__)
# A secret key is needed for session-based flash messages
app.secret_key = "plantpal-secret-key-student-project-2026"

# Ensure the database tables are created at application startup
database.init_db()

# Curated daily gardening tips to display on the dashboard
DAILY_TIPS = [
    "Always check soil moisture with your finger before watering. Overwatering is the #1 cause of houseplant problems!",
    "Rotate your plants 90 degrees every week so they receive balanced light and grow evenly.",
    "Morning is the best time to water plants, allowing excess moisture to evaporate throughout the day.",
    "Wipe plant leaves with a soft damp cloth monthly to clear dust and boost photosynthesis.",
    "Ensure pots have drainage holes so excess water can escape and prevent root rot.",
    "Pinch off spent blooms and yellowing leaves to redirect energy to new, healthy growth."
]


def get_today_tip():
    """Pick a rotating daily tip based on today's day of year."""
    day_num = date.today().timetuple().tm_yday
    return DAILY_TIPS[day_num % len(DAILY_TIPS)]


# -------------------------------------------------------------
# 1. DASHBOARD ROUTE
# -------------------------------------------------------------
@app.route("/")
def dashboard():
    """
    Main dashboard displaying live statistics, upcoming watering reminders,
    pending care tasks, and a daily tip.
    """
    stats = database.get_dashboard_stats()
    today_tip = get_today_tip()
    challenges_summary = database.get_challenges()
    ollama_online, ollama_msg = ai_service.check_ollama_status()

    return render_template(
        "dashboard.html",
        stats=stats,
        today_tip=today_tip,
        challenges=challenges_summary,
        ollama_online=ollama_online,
        ollama_msg=ollama_msg,
        active_page="dashboard"
    )


# -------------------------------------------------------------
# 2. PLANT MANAGEMENT ROUTES
# -------------------------------------------------------------
@app.route("/plants")
def plants():
    """
    View all plants with search query and sunlight filter.
    """
    query = request.args.get("q", "").strip()
    sunlight = request.args.get("sunlight", "all").strip()

    all_plants = database.get_all_plants(search_query=query, sunlight_filter=sunlight)

    return render_template(
        "plants.html",
        plants=all_plants,
        query=query,
        selected_sunlight=sunlight,
        active_page="plants"
    )


@app.route("/plants/new", methods=["GET", "POST"])
def add_plant():
    """
    Add a new plant to the user's garden.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        location = request.form.get("location", "").strip()
        sunlight = request.form.get("sunlight", "Bright Indirect").strip()
        interval = request.form.get("watering_interval_days", "7").strip()
        last_watered = request.form.get("last_watered_date", "").strip()
        notes = request.form.get("notes", "").strip()

        # Basic validation
        if not name or not species:
            flash("Plant nickname and species are required!", "error")
            return redirect(url_for("add_plant"))

        try:
            interval_int = int(interval)
            if interval_int < 1:
                interval_int = 1
        except ValueError:
            interval_int = 7

        if not last_watered:
            last_watered = date.today().strftime("%Y-%m-%d")

        new_id = database.create_plant(
            name=name,
            species=species,
            location=location,
            sunlight=sunlight,
            watering_interval_days=interval_int,
            last_watered_date=last_watered,
            notes=notes
        )

        flash(f"'{name}' has been added to your garden!", "success")
        return redirect(url_for("plant_detail", plant_id=new_id))

    # GET request - prefill last_watered_date to today
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template("plant_form.html", plant=None, today=today_str, active_page="plants")


@app.route("/plants/<int:plant_id>")
def plant_detail(plant_id):
    """
    View individual plant details and persistent watering history.
    """
    plant = database.get_plant(plant_id)
    if not plant:
        flash("Plant not found.", "error")
        return redirect(url_for("plants"))

    history = database.get_watering_history(plant_id)

    return render_template(
        "plant_detail.html",
        plant=plant,
        history=history,
        active_page="plants"
    )


@app.route("/plants/<int:plant_id>/edit", methods=["GET", "POST"])
def edit_plant(plant_id):
    """
    Edit an existing plant's information.
    """
    plant = database.get_plant(plant_id)
    if not plant:
        flash("Plant not found.", "error")
        return redirect(url_for("plants"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        location = request.form.get("location", "").strip()
        sunlight = request.form.get("sunlight", "Bright Indirect").strip()
        interval = request.form.get("watering_interval_days", "7").strip()
        last_watered = request.form.get("last_watered_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if not name or not species:
            flash("Plant nickname and species are required!", "error")
            return redirect(url_for("edit_plant", plant_id=plant_id))

        try:
            interval_int = int(interval)
            if interval_int < 1:
                interval_int = 1
        except ValueError:
            interval_int = 7

        if not last_watered:
            last_watered = plant["last_watered_date"]

        database.update_plant(
            plant_id=plant_id,
            name=name,
            species=species,
            location=location,
            sunlight=sunlight,
            watering_interval_days=interval_int,
            last_watered_date=last_watered,
            notes=notes
        )

        flash(f"Updated '{name}' successfully!", "success")
        return redirect(url_for("plant_detail", plant_id=plant_id))

    today_str = date.today().strftime("%Y-%m-%d")
    return render_template("plant_form.html", plant=plant, today=today_str, active_page="plants")


@app.route("/plants/<int:plant_id>/delete", methods=["POST"])
def delete_plant(plant_id):
    """
    Delete a plant from the database with confirmation.
    """
    plant = database.get_plant(plant_id)
    name = plant["name"] if plant else "Plant"
    database.delete_plant(plant_id)
    flash(f"'{name}' was removed from your garden.", "info")
    return redirect(url_for("plants"))


@app.route("/plants/<int:plant_id>/water", methods=["POST"])
def water_plant(plant_id):
    """
    Action: Mark plant as watered today.
    Supports both traditional POST redirect and JSON response for AJAX.
    """
    plant = database.get_plant(plant_id)
    if not plant:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Plant not found"}), 404
        flash("Plant not found.", "error")
        return redirect(url_for("plants"))

    notes = request.form.get("notes") or request.json.get("notes") if request.is_json else None
    water_date = date.today().strftime("%Y-%m-%d")

    database.log_watering(plant_id, watered_date=water_date, notes=notes)

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        updated_plant = database.get_plant(plant_id)
        return jsonify({
            "success": True,
            "message": f"'{plant['name']}' watered!",
            "next_watering_date": updated_plant["next_watering_date"],
            "status_label": updated_plant["status_label"],
            "status": updated_plant["status"]
        })

    flash(f"Awesome! You watered '{plant['name']}'. Schedule updated.", "success")
    # Redirect back to referring page or plant detail
    next_url = request.form.get("next") or request.referrer or url_for("plant_detail", plant_id=plant_id)
    return redirect(next_url)


# -------------------------------------------------------------
# 3. WATERING SCHEDULER ROUTE
# -------------------------------------------------------------
@app.route("/scheduler")
def scheduler():
    """
    Watering schedule broken down into Overdue, Due Today, and Upcoming.
    """
    data = database.get_scheduler_data()
    return render_template(
        "scheduler.html",
        overdue=data["overdue"],
        due_today=data["due_today"],
        upcoming=data["upcoming"],
        total_count=data["total_count"],
        active_page="scheduler"
    )


# -------------------------------------------------------------
# 4. CARE TASKS ROUTES
# -------------------------------------------------------------
@app.route("/tasks")
def tasks():
    """
    View care tasks with filter for pending and completed.
    """
    filter_status = request.args.get("filter", "all")
    all_tasks = database.get_tasks(filter_status if filter_status in ("pending", "completed") else None)
    all_plants = database.get_all_plants()
    today_str = date.today().strftime("%Y-%m-%d")

    return render_template(
        "tasks.html",
        tasks=all_tasks,
        plants=all_plants,
        filter_status=filter_status,
        today=today_str,
        active_page="tasks"
    )


@app.route("/tasks/new", methods=["POST"])
def add_task():
    """
    Create a new care task.
    """
    title = request.form.get("title", "").strip()
    plant_id_raw = request.form.get("plant_id", "").strip()
    task_type = request.form.get("task_type", "other").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title:
        flash("Task title is required!", "error")
        return redirect(url_for("tasks"))

    if not due_date:
        due_date = date.today().strftime("%Y-%m-%d")

    plant_id = int(plant_id_raw) if plant_id_raw.isdigit() else None

    database.create_task(
        title=title,
        plant_id=plant_id,
        task_type=task_type,
        due_date=due_date
    )

    flash("Care task added!", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """
    Toggle task between pending and completed.
    """
    database.toggle_task(task_id)

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Task updated!", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    """
    Delete a task.
    """
    database.delete_task(task_id)

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Task removed.", "info")
    return redirect(url_for("tasks"))


# -------------------------------------------------------------
# 5. PLANT LIBRARY ROUTES
# -------------------------------------------------------------
@app.route("/library")
def library():
    """
    Explore curated plant guides for 7 popular indoor plants.
    """
    plants_list = plant_library.get_all_library_plants()
    return render_template(
        "library.html",
        library_plants=plants_list,
        active_page="library"
    )


@app.route("/library/add/<plant_slug>", methods=["POST"])
def add_library_plant(plant_slug):
    """
    Instantly add a plant from the library to the user's garden.
    """
    item = plant_library.get_library_plant(plant_slug)
    if not item:
        flash("Plant not found in library.", "error")
        return redirect(url_for("library"))

    nickname = request.form.get("nickname") or f"My {item['name']}"
    location = request.form.get("location") or "Living Room"
    today_str = date.today().strftime("%Y-%m-%d")

    new_id = database.create_plant(
        name=nickname,
        species=item["species"],
        location=location,
        sunlight=item["sunlight"],
        watering_interval_days=item["watering_interval_days"],
        last_watered_date=today_str,
        notes=f"Added from PlantPal Library. {item['care_tips']}"
    )

    flash(f"🎉 '{nickname}' added to your garden!", "success")
    return redirect(url_for("plant_detail", plant_id=new_id))


# -------------------------------------------------------------
# 6. DAILY CHALLENGES ROUTES
# -------------------------------------------------------------
@app.route("/challenges")
def challenges():
    """
    View and complete daily gardening challenges.
    """
    data = database.get_challenges()
    return render_template(
        "challenges.html",
        challenges=data["items"],
        total=data["total"],
        completed_count=data["completed_count"],
        progress_percent=data["progress_percent"],
        active_page="challenges"
    )


@app.route("/challenges/<challenge_key>/toggle", methods=["POST"])
def toggle_challenge(challenge_key):
    """
    Toggle a challenge between complete and incomplete.
    """
    database.toggle_challenge(challenge_key)

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = database.get_challenges()
        return jsonify({
            "success": True,
            "completed_count": data["completed_count"],
            "progress_percent": data["progress_percent"]
        })

    flash("Challenge updated!", "success")
    return redirect(url_for("challenges"))


# -------------------------------------------------------------
# 7. AI ASSISTANT ROUTES
# -------------------------------------------------------------
@app.route("/ai-assistant")
def ai_assistant():
    """
    Interactive chat interface for the SmolLM2 360M AI gardening mentor.
    """
    ollama_online, ollama_msg = ai_service.check_ollama_status()
    return render_template(
        "ai_assistant.html",
        ollama_online=ollama_online,
        ollama_msg=ollama_msg,
        active_page="ai"
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Backend endpoint for sending queries to SmolLM2 360M via Ollama.
    Returns JSON with the response and transparent metadata.
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Message cannot be empty."
        }), 400

    result = ai_service.ask_gardening_assistant(message)
    return jsonify({
        "success": True,
        **result
    })


@app.route("/api/status")
def api_status():
    """
    Health check endpoint reporting Ollama and model status.
    """
    online, msg = ai_service.check_ollama_status()
    return jsonify({
        "ollama_online": online,
        "message": msg,
        "model": ai_service.MODEL_NAME
    })


# -------------------------------------------------------------
# ERROR HANDLERS (Safe, user-friendly responses)
# -------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Run development server on port 5000
    print("🌱 PlantPal is starting on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
