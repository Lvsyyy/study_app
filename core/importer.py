"""Bulk-import questions from a JSON file.

Format: a list of objects, e.g.
  {"subject": "Math", "topic": "Binary", "question": "Convert 101101 to decimal.",
   "answer": "45", "alt_answers": ["45.0"], "hint": "...", "image": "diagram.png",
   "difficulty": 2}
`image` may be relative to the JSON file; it is copied into the app's assets folder.
"""
import json
from pathlib import Path

from core.paths import store_image

REQUIRED = ("subject", "topic", "question", "answer")


def load_questions(path, valid_subjects):
    """Parse and validate. Returns (questions, errors); nothing is written."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"Could not read file: {exc}"]
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list):
        return [], ["Expected a JSON list of questions."]

    questions, errors = [], []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            errors.append(f"#{index}: not an object")
            continue
        missing = [
            k for k in REQUIRED
            if item.get(k) is None or not str(item.get(k)).strip()
        ]
        if missing:
            errors.append(f"#{index}: missing {', '.join(missing)}")
            continue
        subject = item["subject"]
        if not isinstance(subject, str) or subject not in valid_subjects:
            errors.append(f"#{index}: unknown or invalid subject '{subject}'")
            continue
        difficulty = item.get("difficulty", 1)
        if type(difficulty) is not int or not 1 <= difficulty <= 5:
            errors.append(f"#{index}: difficulty must be 1-5")
            continue
        question_type = item.get("question_type", "text")
        if not isinstance(question_type, str) or question_type not in ("text", "code", "batch"):
            errors.append(f"#{index}: question_type must be 'text', 'code' or 'batch'")
            continue
        alts = item.get("alt_answers") or []
        if not isinstance(alts, list):
            errors.append(f"#{index}: alt_answers must be a list")
            continue
        image = item.get("image")
        if image:
            if not isinstance(image, str):
                errors.append(f"#{index}: image path must be a string")
                continue
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = path.parent / image_path
            if not image_path.is_file():
                errors.append(f"#{index}: image not found: {image}")
                continue
            image = str(image_path)
        questions.append({
            "subject_name": item["subject"].strip(),
            "topic_name": str(item["topic"]).strip(),
            "question_text": str(item["question"]).strip(),
            "answer": str(item["answer"]).strip(),
            "alt_answers": [str(a).strip() for a in alts if str(a).strip()],
            "hint": (str(item["hint"]).strip() or None) if item.get("hint") else None,
            "question_image": image,
            "difficulty": difficulty,
            "question_type": question_type,
        })
    return questions, errors


def import_file(path, question_repository):
    """All-or-nothing import. Returns (imported_count, errors)."""
    valid = {row["name"] for row in question_repository.list_subjects()}
    questions, errors = load_questions(path, valid)
    if errors or not questions:
        return 0, errors or ["The file contains no questions."]

    stored_images = []
    try:
        for question in questions:
            if question["question_image"]:
                stored = store_image(question["question_image"])
                stored_images.append(stored)
                question["question_image"] = stored
        question_repository.add_questions(questions)
    except Exception:
        for stored in stored_images:
            Path(stored).unlink(missing_ok=True)
        raise
    return len(questions), []
