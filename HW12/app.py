from __future__ import annotations

import csv
from pathlib import Path
from threading import Lock
from typing import Any

from flask import Flask, jsonify, request

app = Flask(__name__)

# CSV-файл зберігається в тій самій папці, що й app.py.
CSV_FILE = Path(__file__).with_name("students.csv")
FIELDNAMES = ["id", "name", "surname", "age"]
FILE_LOCK = Lock()


def ensure_csv_file() -> None:
    """Створює CSV-файл із заголовками, якщо його ще немає."""
    if not CSV_FILE.exists():
        with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_students() -> list[dict[str, Any]]:
    """Зчитує всіх студентів із CSV-файлу."""
    ensure_csv_file()
    students: list[dict[str, Any]] = []

    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row.get("id"):
                continue

            students.append(
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "surname": row["surname"],
                    "age": int(row["age"]),
                }
            )

    return students


def write_students(students: list[dict[str, Any]]) -> None:
    """Повністю перезаписує CSV-файл актуальними даними."""
    with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(students)


def error_response(message: str, status_code: int):
    """Формує однакову JSON-відповідь для помилок."""
    return jsonify({"error": message}), status_code


def get_json_body() -> dict[str, Any] | None:
    """Повертає JSON-тіло запиту або None, якщо воно некоректне."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def validate_fields(
    data: dict[str, Any] | None,
    allowed_fields: set[str],
    required_fields: set[str],
) -> tuple[str | None, int | None]:
    """Перевіряє наявність обов'язкових та відсутність зайвих полів."""
    if not data:
        return "Тіло запиту порожнє або не містить коректний JSON.", 400

    received_fields = set(data.keys())
    unknown_fields = received_fields - allowed_fields
    if unknown_fields:
        fields = ", ".join(sorted(unknown_fields))
        return f"Передано неіснуючі поля: {fields}.", 400

    missing_fields = required_fields - received_fields
    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        return f"Не передано обов'язкові поля: {fields}.", 400

    return None, None


def validate_name(value: Any, field_name: str) -> tuple[str | None, str | None]:
    """Перевіряє ім'я або прізвище та повертає очищене значення."""
    if not isinstance(value, str) or not value.strip():
        return None, f"Поле '{field_name}' повинно бути непорожнім рядком."
    return value.strip(), None


def validate_age(value: Any) -> tuple[int | None, str | None]:
    """Перевіряє вік студента."""
    if isinstance(value, bool):
        return None, "Поле 'age' повинно бути цілим числом."

    try:
        age = int(value)
    except (TypeError, ValueError):
        return None, "Поле 'age' повинно бути цілим числом."

    if age <= 0 or age > 150:
        return None, "Поле 'age' повинно бути в межах від 1 до 150."

    return age, None


def find_student_index(students: list[dict[str, Any]], student_id: int) -> int | None:
    """Повертає індекс студента у списку за його ID."""
    for index, student in enumerate(students):
        if student["id"] == student_id:
            return index
    return None


@app.get("/students")
def get_students():
    """Повертає всіх студентів або студентів за прізвищем."""
    students = read_students()
    surname = request.args.get("surname", type=str)

    if surname is None:
        return jsonify(students), 200

    surname = surname.strip()
    if not surname:
        return error_response("Прізвище не може бути порожнім.", 400)

    found_students = [
        student
        for student in students
        if student["surname"].casefold() == surname.casefold()
    ]

    if not found_students:
        return error_response(
            f"Студентів із прізвищем '{surname}' не знайдено.", 404
        )

    return jsonify(found_students), 200


@app.get("/students/<int:student_id>")
def get_student_by_id(student_id: int):
    """Повертає одного студента за ID."""
    students = read_students()
    index = find_student_index(students, student_id)

    if index is None:
        return error_response(f"Студента з ID {student_id} не знайдено.", 404)

    return jsonify(students[index]), 200


@app.get("/students/surname/<string:surname>")
def get_students_by_surname(surname: str):
    """Додатковий варіант GET-запиту пошуку за прізвищем."""
    students = read_students()
    surname = surname.strip()

    found_students = [
        student
        for student in students
        if student["surname"].casefold() == surname.casefold()
    ]

    if not found_students:
        return error_response(
            f"Студентів із прізвищем '{surname}' не знайдено.", 404
        )

    return jsonify(found_students), 200


@app.post("/students")
def create_student():
    """Створює нового студента та автоматично призначає йому ID."""
    data = get_json_body()
    allowed_fields = {"name", "surname", "age"}
    error, status = validate_fields(data, allowed_fields, allowed_fields)
    if error:
        return error_response(error, status or 400)

    assert data is not None

    name, name_error = validate_name(data["name"], "name")
    if name_error:
        return error_response(name_error, 400)

    surname, surname_error = validate_name(data["surname"], "surname")
    if surname_error:
        return error_response(surname_error, 400)

    age, age_error = validate_age(data["age"])
    if age_error:
        return error_response(age_error, 400)

    with FILE_LOCK:
        students = read_students()
        new_id = max((student["id"] for student in students), default=0) + 1
        new_student = {
            "id": new_id,
            "name": name,
            "surname": surname,
            "age": age,
        }
        students.append(new_student)
        write_students(students)

    return (
        jsonify(
            {
                "message": "Студента успішно додано.",
                "student": new_student,
            }
        ),
        201,
    )


@app.put("/students/<int:student_id>")
def update_student(student_id: int):
    """Оновлює передані поля: ім'я, прізвище та/або вік студента."""
    data = get_json_body()
    allowed_fields = {"name", "surname", "age"}
    error, status = validate_fields(data, allowed_fields, set())
    if error:
        return error_response(error, status or 400)

    assert data is not None
    updates: dict[str, Any] = {}

    if "name" in data:
        name, name_error = validate_name(data["name"], "name")
        if name_error:
            return error_response(name_error, 400)
        updates["name"] = name

    if "surname" in data:
        surname, surname_error = validate_name(data["surname"], "surname")
        if surname_error:
            return error_response(surname_error, 400)
        updates["surname"] = surname

    if "age" in data:
        age, age_error = validate_age(data["age"])
        if age_error:
            return error_response(age_error, 400)
        updates["age"] = age

    with FILE_LOCK:
        students = read_students()
        index = find_student_index(students, student_id)

        if index is None:
            return error_response(f"Студента з ID {student_id} не знайдено.", 404)

        students[index].update(updates)
        updated_student = students[index]
        write_students(students)

    return jsonify(
        {
            "message": "Дані студента успішно оновлено.",
            "student": updated_student,
        }
    ), 200


@app.patch("/students/<int:student_id>")
def update_student_age(student_id: int):
    """Оновлює тільки вік студента за його ID."""
    data = get_json_body()
    allowed_fields = {"age"}
    error, status = validate_fields(data, allowed_fields, allowed_fields)
    if error:
        return error_response(error, status or 400)

    assert data is not None
    age, age_error = validate_age(data["age"])
    if age_error:
        return error_response(age_error, 400)

    with FILE_LOCK:
        students = read_students()
        index = find_student_index(students, student_id)

        if index is None:
            return error_response(f"Студента з ID {student_id} не знайдено.", 404)

        students[index]["age"] = age
        updated_student = students[index]
        write_students(students)

    return jsonify(
        {
            "message": "Вік студента успішно оновлено.",
            "student": updated_student,
        }
    ), 200


@app.delete("/students/<int:student_id>")
def delete_student(student_id: int):
    """Видаляє студента з CSV-файлу за його ID."""
    with FILE_LOCK:
        students = read_students()
        index = find_student_index(students, student_id)

        if index is None:
            return error_response(f"Студента з ID {student_id} не знайдено.", 404)

        deleted_student = students.pop(index)
        write_students(students)

    return jsonify(
        {
            "message": "Студента успішно видалено.",
            "student": deleted_student,
        }
    ), 200


if __name__ == "__main__":
    ensure_csv_file()
    app.run(host="127.0.0.1", port=5000, debug=True)
