# 🌱 PlantPal — AI Gardening Assistant

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass]*

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Ollama](https://img.shields.io/badge/AI-SmolLM2--360M-black?logo=ollama&logoColor=white)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **PlantPal** is a lightweight, privacy-first web application designed to help urban plant lovers and beginners keep their indoor sanctuaries thriving. Powered by a local **SmolLM2 360M** model running via Ollama, PlantPal provides personalized gardening advice, automatic watering schedules, task checklists, and daily nature challenges—all without subscriptions, trackers, or cloud dependencies.

---

## 🍃 Why PlantPal? ("Touch Grass" Theme)

In an era of endless screen time, the **Hacktoberfest "Touch Grass"** challenge asks us to use technology to reconnect with the real world. 

**PlantPal** turns your desk or balcony into an interactive green sanctuary:
- **Build Real Habits:** Daily micro-challenges prompt you to step away from monitors, inspect soil moisture with your fingers, observe leaf health, and spend mindful time outdoors.
- **Save Plants with Math & AI:** Overwatering is the #1 killer of houseplants. PlantPal calculates dynamic watering cycles and answers tricky plant health questions in real-time.
- **100% Private & Local AI:** Your garden notes and chat queries stay on your local machine. No paid OpenAI API keys or cloud telemetry required.

---

## ✨ Core Features

### 1. 📊 Live Garden Dashboard
- **Real-Time Database Metrics:** Instant statistics for total plants, plants due for hydration, pending care tasks, and completed tasks.
- **Smart Upcoming Reminders:** Highlights which plants need water next, complete with status tags (`Overdue`, `Due Today`, `Upcoming`) and quick one-click water buttons.
- **Rotating Daily Tip:** Curated advice covering proper watering times, light angles, and soil care.

### 2. 🌿 Comprehensive Plant Management
- **Full CRUD Operations:** Add, view, edit, and delete plants with custom nicknames, botanical species, sunlight requirements, watering intervals, room locations, and notes.
- **Live Search & Filter:** Instantly filter your collection by name, room, or sunlight level.
- **Persistent Watering History:** Every watering session is logged in SQLite with timestamps and optional observation notes.

### 3. 💧 Smart Watering Scheduler
- **Dynamic Date Calculations:** Calculates the exact next watering date based on interval history (`next_date = last_watered + interval`).
- **Urgency Buckets:** Automatically sorts plants into **Overdue**, **Due Today**, and **Upcoming**.
- **AJAX "Water Now" Action:** Update plant schedules asynchronously without reloading the page.

### 4. 📋 Care Tasks Checklist
- **Organized Maintenance:** Track pruning, fertilizing, repotting, wiping dust, or checking sunlight.
- **Plant Linkage:** Associate tasks with specific plants in your garden or keep them as general gardening chores.
- **One-Click Toggles:** Mark tasks complete and filter by `All`, `Pending`, or `Completed`.

### 5. 📚 Botanical Plant Library
Includes built-in reference care guides for 7 popular home plants:
1. **Money Plant / Golden Pothos** (*Epipremnum aureum*)
2. **Snake Plant** (*Sansevieria trifasciata*)
3. **Aloe Vera** (*Aloe barbadensis miller*)
4. **Spider Plant** (*Chlorophytum comosum*)
5. **Peace Lily** (*Spathiphyllum wallisii*)
6. **Tulsi / Holy Basil** (*Ocimum sanctum*)
7. **Areca Palm** (*Dypsis lutescens*)
- **1-Click Import:** Add any library plant directly to your personal collection with sensible care defaults!

### 6. 🏆 Daily "Touch Grass" Challenges
- Five daily mindfulness activities:
  - 🔍 *Check soil moisture with the finger test*
  - 🍃 *Observe leaf health and dust top foliage*
  - 📖 *Learn one new botanical fact*
  - ☀️ *Spend 10 minutes outdoors caring for plants*
  - ✂️ *Propagate a cutting in water or soil*
- Live progress bar that tracks completion percentage.

### 7. 🤖 Local SmolLM2 360M AI Mentor
- Runs locally through **Ollama's HTTP API** (`http://127.0.0.1:11434`).
- Optimized prompt engineering designed specifically for small language models.
- **Transparent Fallback Architecture:** If Ollama is offline or times out, the app automatically serves verified botanical handbook advice labeled as `🌿 Verified Gardening Guide (Offline Fallback)`. The app never fabricates an AI response or locks up.

---

## 🏗️ System Architecture

```text
[ Browser / Mobile Client ]
         │
         ▼  (HTTP / JSON AJAX)
┌────────────────────────────────────────────────────────┐
│               Flask Backend (app.py)                   │
├──────────────────────────┬─────────────────────────────┤
│   Database Layer         │     AI Service Integration  │
│   (database.py)          │     (ai_service.py)         │
│   - SQLite Connection    │     - Ollama REST Client    │
│   - Parameterized SQL    │     - Prompt Template       │
│   - Date Math & History  │     - Transparent Fallback  │
└────────────┬─────────────┴──────────────┬──────────────┘
             │                            │
             ▼                            ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   SQLite Database        │  │   Local Ollama Engine    │
│   (instance/plantpal.db) │  │   Model: smollm2:360m    │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Modern CSS3, Vanilla JS | Zero build steps, beginner-friendly, high performance, and accessible. |
| **Styling** | Nature-Inspired Design System | Forest green (`#2D5A27`), sage (`#5B8A61`), warm cream (`#FAF9F5`), and soft cards. |
| **Backend** | Python 3.12 + Flask 3.1 | Clean, readable REST routing and templating. |
| **Database** | SQLite3 | Zero-configuration, serverless, ACID-compliant local storage. |
| **AI Model** | SmolLM2 360M via Ollama | Lightweight (~725 MB), fast local CPU inference, privacy-preserving. |

---

## 🚀 Quickstart Guide

### Prerequisites
1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/) *(make sure to check "Add python.exe to PATH")*.
2. **Ollama**: Download from [ollama.com](https://ollama.com/download).

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/plantpal.git
cd plantpal
```

### 2. Pull the Lightweight AI Model
In your terminal, pull the SmolLM2 360M model using Ollama:
```bash
ollama pull smollm2:360m
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 Running the Test Suite

PlantPal includes an automated test suite verifying all 8 core system requirements:
- Flask and empty database boot
- Plant CRUD, search, and filtering
- Date math and watering status transitions (`overdue` ➔ `upcoming`)
- Care task creation and toggles
- Plant library 1-click import
- Daily challenge progress calculations
- Live Ollama SmolLM2 generation & transparent offline fallback
- SQLite persistence across sessions

Run the test suite with:
```bash
python test_app.py
```

Expected output:
```text
==============================================
[TEST] RUNNING PLANTPAL COMPREHENSIVE TEST SUITE
==============================================
  [PASS] Test 1: Flask and dashboard start with empty database
  [PASS] Test 2: Plant creation, detail view, search, and editing work
  [PASS] Test 3: Watering date math, overdue categorization, and watering logs work
  [PASS] Test 4: Care task creation, listing, and toggle work
  [PASS] Test 5: Plant library loads 7 species and imports to garden
  [PASS] Test 6: Daily challenges toggle and progress tracking work
  [PASS] Test 7: AI Assistant local SmolLM2 model & transparent fallback work
  [PASS] Test 8: SQLite database persistence verified

[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!
```

---

## 📁 Repository Structure

```text
plantpal/
├── app.py                  # Main Flask application and REST routes
├── database.py             # SQLite schema, queries, and schedule calculations
├── plant_library.py        # Curated care data for 7 indoor plant species
├── ai_service.py           # Ollama SmolLM2 client and transparent fallback
├── requirements.txt        # Flask and requests dependencies
├── test_app.py             # Automated unit and integration test suite
├── .gitignore              # Ignores database files, caches, and environments
├── instance/
│   └── .gitkeep            # Database directory placeholder
├── templates/
│   ├── base.html           # Shared layout with responsive sidebar and toasts
│   ├── dashboard.html      # Metrics, watering reminders, and quick actions
│   ├── plants.html         # Plant collection with search and sunlight filter
│   ├── plant_form.html     # Add/edit plant form
│   ├── plant_detail.html   # Detailed plant profile and watering history
│   ├── scheduler.html      # Categorized watering schedule
│   ├── tasks.html          # Care tasks checklist and status filter
│   ├── library.html        # Plant library reference cards
│   ├── challenges.html     # Daily gardening habit challenges
│   ├── ai_assistant.html   # Interactive chat interface with prompt chips
│   ├── 404.html            # Custom 404 error page
│   └── 500.html            # Custom 500 error page
└── static/
    ├── css/
    │   └── style.css       # Nature-inspired responsive CSS design system
    └── js/
        └── app.js          # AJAX updates, mobile navigation, and chat logic
```

---

## 🛡️ Privacy & Ethical AI Principles

1. **No Data Harvesting:** All plant data, notes, and photos stay on your local device in `instance/plantpal.db`.
2. **Offline-First Resilience:** If you have no internet or Ollama is shut down, PlantPal remains 100% operational with its curated fallback knowledge base.
3. **No AI Hallucination Masquerading:** The assistant transparently tags whether a response was generated by **SmolLM2 360M** or retrieved from the **Verified Gardening Guide**.

---

## 👨‍💻 Student Author Note

Built with ❤️ by a **second-year IT engineering student** as an open-source project for **Hacktoberfest 2026**.

The codebase prioritizes clear naming, clean architecture, parameterized database queries, and zero unnecessary dependencies to make it beginner-friendly and educational.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
Feel free to fork, experiment, and help people touch more grass!
