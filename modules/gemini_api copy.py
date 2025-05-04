import os
import json
import pandas as pd
import google.generativeai as genai
from google.generativeai import chat

from dotenv import load_dotenv

# --- 1) Initialization at import time ---
load_dotenv()
_api_key = os.getenv("GOOGLE_API_KEY")
if not _api_key:
    raise RuntimeError("GOOGLE_API_KEY not found in environment.")
genai.configure(api_key=_api_key)  # Picks up from env var if not passed explicitly :contentReference[oaicite:0]{index=0}

# --- 2) Load datasets once ---
_students_df = pd.read_csv("dataset/dataset_etudiants.csv")
_courses_df  = pd.read_csv("dataset/cours.csv")

def get_course_recommendations(student_query):
    """
    Fetch course recommendations for a given student.

    Args:
        student_query (int or str):
            If int or numeric string: treated as student ID.
            Otherwise: partial, case-insensitive student name.

    Returns:
        dict: JSON-like dict with key "recommendations" and a list of objects
              each containing 'course_id', 'course_name', and 'reason'.
    """
    # 1) Lookup student
    if isinstance(student_query, int) or (isinstance(student_query, str) and student_query.isdigit()):
        sid = int(student_query)
        df = _students_df[_students_df["id"] == sid]
    else:
        df = _students_df[_students_df["name"].str.contains(str(student_query),
                                                            case=False, na=False)]
    if df.empty:
        raise ValueError(f"No student found for query: {student_query!r}")
    student = df.iloc[0].to_dict()

    # 2) Construct system + user messages
    system_message = {
        "role": "system",
        "content": (
            "You are an academic adviser. Given a student record (with their grades"
            " and interests) and a catalog of courses (each with prerequisites,"
            " topics, level), recommend 3–5 courses. Output must be strictly valid"
            " JSON with a top-level key 'recommendations' whose value is a list"
            " of objects with 'course_id', 'course_name', and 'reason'. Do not"
            " output any other text."
        )
    }
    user_message = {
        "role": "user",
        "content": {
            "student": student,
            "courses": _courses_df.to_dict(orient="records")
        }
    }

    # 3) Call the Gemini chat completions API
    response = chat.completions.create(
        model="gemini-2.0-flash",
        messages=[system_message, user_message]
    )  # Uses Chat Completions API :contentReference[oaicite:1]{index=1}

    # 4) Parse and return JSON
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from model:\n{raw}")

# Example usage
if __name__ == "__main__":
    sid = input("Enter student ID or name: ").strip()
    try:
        recs = get_course_recommendations(sid)
        print(json.dumps(recs, indent=2, ensure_ascii=False))
    except Exception as e:
        print("❌", e, file=sys.stderr)
        sys.exit(1)
