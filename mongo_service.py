import json
from pathlib import Path
from pymongo import MongoClient

# 1. Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["AutoAssessDB"]
collection = db["student_answers"]


def store_student_data(json_path: str, student_id: str, exam_id: str = "EXAM_01"):
    """Reads segmented JSON output and saves it into MongoDB."""
    path = Path(json_path)
    if not path.exists():
        print(f"[-] Error: Could not find '{json_path}'. Make sure you ran 'python -m src.main' first.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    document = {
        "student_id": student_id,
        "student_name": data.get("student", path.stem),
        "exam_id": exam_id,
        "answers": data.get("answers", {})
    }

    # Upsert: Update if exists, insert if new
    collection.update_one(
        {"student_id": student_id, "exam_id": exam_id},
        {"$set": document},
        upsert=True
    )
    print(f"[+] Successfully saved {student_id} to MongoDB database 'AutoAssessDB'!")


def retrieve_by_id(student_id: str):
    """Retrieves record by student ID."""
    return collection.find_one({"student_id": student_id}, {"_id": 0})


def retrieve_by_name(student_name: str):
    """Retrieves record by student name."""
    return collection.find_one({"student_name": student_name}, {"_id": 0})


# --- THIS CODE RUNS WHEN YOU EXECUTE THE SCRIPT ---
if __name__ == "__main__":
    print("--- 1. Storing Data ---")
    store_student_data(
        json_path="output/student1.json",
        student_id="STU_001",
        exam_id="PYTHON_TEST"
    )

    print("\n--- 2. Retrieving by Student ID (STU_001) ---")
    data_by_id = retrieve_by_id("STU_001")
    print(data_by_id)

    print("\n--- 3. Retrieving by Student Name (student1) ---")
    data_by_name = retrieve_by_name("student1")
    print(data_by_name)