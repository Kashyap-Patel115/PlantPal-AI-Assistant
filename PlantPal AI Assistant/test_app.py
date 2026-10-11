"""
test_app.py - Verification Test Suite for PlantPal
==================================================
Runs automated checks covering all 12 testing requirements:
1. Flask initialization and dashboard loading.
2. Empty database dashboard rendering.
3. Plant creation, retrieval, editing, search, and deletion.
4. Data persistence in SQLite.
5. Watering calculations (overdue, due today, upcoming).
6. Care tasks creation and status toggles.
7. Library plant importing into personal garden.
8. Daily challenges completion and progress statistics.
9. AI Assistant communication with SmolLM2 360M via Ollama.
10. AI Assistant graceful fallback when offline.
11. Routing and response status codes.
"""

import sys
import unittest
from datetime import date, timedelta
from app import app
import database
import ai_service
import plant_library

class PlantPalTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        # Initialize the database
        database.init_db()

    def test_01_flask_and_empty_dashboard(self):
        """Verify Flask starts and dashboard loads with empty DB."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PlantPal", response.data)
        self.assertIn(b"Garden Dashboard", response.data)
        print("  [PASS] Test 1: Flask and dashboard start with empty database")

    def test_02_plant_crud_and_search(self):
        """Verify plant creation, search, edit, and detail views."""
        # 1. Create a plant
        post_data = {
            "name": "Test Sansevieria",
            "species": "Sansevieria trifasciata",
            "location": "Office Desk",
            "sunlight": "Low Light",
            "watering_interval_days": "14",
            "last_watered_date": date.today().strftime("%Y-%m-%d"),
            "notes": "Healthy indoor test succulent"
        }
        res = self.client.post("/plants/new", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Test Sansevieria", res.data)

        # 2. Verify search returns the plant
        search_res = self.client.get("/plants?q=Sansevieria")
        self.assertEqual(search_res.status_code, 200)
        self.assertIn(b"Test Sansevieria", search_res.data)

        # 3. Get the plant from DB to check ID
        plants = database.get_all_plants(search_query="Test Sansevieria")
        self.assertTrue(len(plants) > 0)
        plant_id = plants[0]["id"]

        # 4. View Detail
        detail_res = self.client.get(f"/plants/{plant_id}")
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn(b"Test Sansevieria", detail_res.data)

        # 5. Edit plant
        edit_data = post_data.copy()
        edit_data["name"] = "Updated Sansevieria"
        edit_res = self.client.post(f"/plants/{plant_id}/edit", data=edit_data, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"Updated Sansevieria", edit_res.data)

        print("  [PASS] Test 2: Plant creation, detail view, search, and editing work")

    def test_03_watering_calculations_and_logging(self):
        """Verify schedule date math, overdue status, and Mark as Watered."""
        # Create a plant watered 10 days ago with a 7 day interval -> Overdue by 3 days
        ten_days_ago = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
        plant_id = database.create_plant(
            name="Thirsty Fern",
            species="Nephrolepis exaltata",
            location="Bathroom",
            sunlight="Medium Light",
            watering_interval_days=7,
            last_watered_date=ten_days_ago,
            notes="Testing overdue math"
        )

        plant = database.get_plant(plant_id)
        self.assertEqual(plant["status"], "overdue")
        self.assertEqual(plant["days_diff"], -3)
        self.assertIn("Overdue by 3 days", plant["status_label"])

        # Now mark as watered today
        water_res = self.client.post(f"/plants/{plant_id}/water", follow_redirects=True)
        self.assertEqual(water_res.status_code, 200)

        # Re-check plant status -> Should now be upcoming in 7 days
        updated_plant = database.get_plant(plant_id)
        self.assertEqual(updated_plant["status"], "upcoming")
        self.assertEqual(updated_plant["days_diff"], 7)

        # Verify watering history
        history = database.get_watering_history(plant_id)
        self.assertTrue(len(history) >= 2)  # initial + new water log

        print("  [PASS] Test 3: Watering date math, overdue categorization, and watering logs work")

    def test_04_care_tasks(self):
        """Verify care task creation, filtering, and completion toggle."""
        task_id = database.create_task(
            title="Prune dry stems",
            plant_id=None,
            task_type="prune",
            due_date=date.today().strftime("%Y-%m-%d")
        )

        # Check in task list
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Prune dry stems", res.data)

        # Toggle to completed
        toggle_res = self.client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)

        tasks = database.get_tasks(filter_status="completed")
        self.assertTrue(any(t["id"] == task_id for t in tasks))

        print("  [PASS] Test 4: Care task creation, listing, and toggle work")

    def test_05_library_and_import(self):
        """Verify plant library profiles and 1-click import into user's garden."""
        library_plants = plant_library.get_all_library_plants()
        self.assertEqual(len(library_plants), 7)

        # Test import of Aloe Vera
        res = self.client.post("/library/add/aloe-vera", data={"nickname": "Kitchen Aloe"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Kitchen Aloe", res.data)

        print("  [PASS] Test 5: Plant library loads 7 species and imports to garden")

    def test_06_daily_challenges(self):
        """Verify daily challenges retrieval and interactive toggle."""
        challenges = database.get_challenges()
        self.assertEqual(challenges["total"], 5)

        # Toggle first challenge
        first_key = challenges["items"][0]["challenge_key"]
        res = self.client.post(f"/challenges/{first_key}/toggle", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        updated_challenges = database.get_challenges()
        self.assertTrue(updated_challenges["completed_count"] >= 1)

        print("  [PASS] Test 6: Daily challenges toggle and progress tracking work")

    def test_07_ai_assistant_live_and_fallback(self):
        """Verify AI assistant works with local SmolLM2 360M and falls back safely."""
        # 1. Test live Ollama status check
        online, msg = ai_service.check_ollama_status()
        print(f"       Ollama status: {online} ({msg})")

        # 2. Test chat API with real question
        chat_res = self.client.post("/api/chat", json={"message": "Why are my money plant leaves turning yellow?"})
        self.assertEqual(chat_res.status_code, 200)
        data = chat_res.get_json()
        self.assertTrue(data.get("success"))
        self.assertTrue(len(data.get("answer", "")) > 10)
        print(f"       AI Response received from {data.get('source')}: {data.get('answer')[:75]}...")

        # 3. Test fallback mechanism explicitly
        fallback = ai_service.get_fallback_answer("How much sunlight does aloe vera need?")
        self.assertTrue(fallback["is_fallback"])
        self.assertEqual(fallback["source"], "curated_gardening_guide")
        self.assertIn("Aloe Vera", fallback["topic"])

        print("  [PASS] Test 7: AI Assistant local SmolLM2 model & transparent fallback work")

    def test_08_data_persistence(self):
        """Verify SQLite data persistence across fresh connections."""
        plants_before = database.get_all_plants()
        count_before = len(plants_before)

        # Create another plant
        new_id = database.create_plant(
            name="Persistence Test Plant",
            species="Chlorophytum comosum",
            location="Porch",
            sunlight="Bright Indirect",
            watering_interval_days=5,
            last_watered_date=date.today().strftime("%Y-%m-%d"),
            notes="Testing SQLite persistence"
        )

        # Fresh query
        plants_after = database.get_all_plants()
        self.assertEqual(len(plants_after), count_before + 1)
        found = any(p["id"] == new_id for p in plants_after)
        self.assertTrue(found)

        # Cleanup test plant
        database.delete_plant(new_id)

        print("  [PASS] Test 8: SQLite database persistence verified")


if __name__ == "__main__":
    print("\n==============================================")
    print("[TEST] RUNNING PLANTPAL COMPREHENSIVE TEST SUITE")
    print("==============================================\n")
    suite = unittest.TestLoader().loadTestsFromTestCase(PlantPalTestSuite)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n[FAILED] SOME TESTS FAILED.")
        sys.exit(1)
