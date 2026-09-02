import json
from pathlib import Path
from pymongo import MongoClient

# 1. Connect to Local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["AutoAssessDB"]
collection = db["student_answers"]


def store_student_data(json_file_path: str, exam_id: str = "PYTHON_TEST"):
    """Reads a segmented student JSON file and stores it into MongoDB."""
    path = Path(json_file_path)

    if not path.exists():
        print(f"[-] File not found: {json_file_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    student_name = data.get("student", path.stem)
    student_id = f"STU_{student_name.upper()}"

    document = {
        "student_id": student_id,
        "student_name": student_name,
        "exam_id": exam_id,
        "answers": data.get("answers", {}),
    }

    # Upsert: updates if already exists, inserts if new
    collection.update_one(
        {"student_id": student_id, "exam_id": exam_id},
        {"$set": document},
        upsert=True,
    )
    print(f"[+] Successfully stored {student_name} ({student_id}) into MongoDB!")


def get_student_by_id(student_id: str):
    """Retrieves stored segmented data for a specific student."""
    return collection.find_one({"student_id": student_id}, {"_id": 0})


if __name__ == "__main__":
    # Ingest student 1
    store_student_data("output/student1.json")

    # Ingest student 2 (if available)
    if Path("output/student2.json").exists():
        store_student_data("output/student2.json")

    # Test retrieval verification
    print("\n--- Testing Retrieval from MongoDB ---")
    record = get_student_by_id("STU_STUDENT1")
    if record:
        print(f"Retrieved: {record['student_name']}")
        print(f"Questions in DB: {list(record['answers'].keys())}")
    else:
        print("[-] Student record not found.")