from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:5000"
RESULTS_FILE = Path(__file__).with_name("results.txt")
TIMEOUT = 5

results: list[str] = []


def format_response(response: requests.Response) -> str:
    """Перетворює відповідь сервера на зручний текст."""
    try:
        body: Any = response.json()
        formatted_body = json.dumps(body, ensure_ascii=False, indent=2)
    except ValueError:
        formatted_body = response.text

    return (
        f"HTTP status: {response.status_code}\n"
        f"Відповідь:\n{formatted_body}"
    )


def save_result(title: str, response: requests.Response) -> None:
    """Виводить результат у консоль та додає його до results.txt."""
    block = f"\n{'=' * 70}\n{title}\n{'=' * 70}\n{format_response(response)}\n"
    print(block)
    results.append(block)


def send_request(
    title: str,
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> requests.Response:
    """Надсилає HTTP-запит та одразу зберігає результат."""
    response = requests.request(
        method=method,
        url=f"{BASE_URL}{endpoint}",
        timeout=TIMEOUT,
        **kwargs,
    )
    save_result(title, response)
    return response


def extract_created_id(response: requests.Response) -> int:
    """Отримує ID створеного студента з відповіді POST."""
    data = response.json()
    return int(data["student"]["id"])


def main() -> None:
    created_ids: list[int] = []

    try:
        # 1. Отримати всіх наявних студентів.
        send_request(
            "1. Отримати всіх наявних студентів (GET)",
            "GET",
            "/students",
        )

        # 2. Створити трьох студентів.
        students_to_create = [
            {"name": "Іван", "surname": "Петренко", "age": 20},
            {"name": "Марія", "surname": "Шевченко", "age": 19},
            {"name": "Олександр", "surname": "Коваль", "age": 21},
        ]

        for number, student in enumerate(students_to_create, start=1):
            response = send_request(
                f"2.{number}. Створити студента (POST)",
                "POST",
                "/students",
                json=student,
            )
            response.raise_for_status()
            created_ids.append(extract_created_id(response))

        first_id, second_id, third_id = created_ids

        # 3. Повторно отримати всіх студентів.
        send_request(
            "3. Отримати інформацію про всіх наявних студентів (GET)",
            "GET",
            "/students",
        )

        # 4. Оновити вік другого студента.
        send_request(
            "4. Оновити вік другого студента (PATCH)",
            "PATCH",
            f"/students/{second_id}",
            json={"age": 25},
        )

        # 5. Отримати інформацію про другого студента за прізвищем.
        send_request(
            "5. Отримати інформацію про другого студента за прізвищем (GET)",
            "GET",
            "/students",
            params={"surname": "Шевченко"},
        )

        # 6. Оновити ім'я, прізвище та вік третього студента.
        send_request(
            "6. Оновити ім'я, прізвище та вік третього студента (PUT)",
            "PUT",
            f"/students/{third_id}",
            json={
                "name": "Андрій",
                "surname": "Мельник",
                "age": 23,
            },
        )

        # 7. Отримати інформацію про третього студента за ID.
        send_request(
            "7. Отримати інформацію про третього студента (GET)",
            "GET",
            f"/students/{third_id}",
        )

        # 8. Отримати всіх наявних студентів.
        send_request(
            "8. Отримати всіх наявних студентів (GET)",
            "GET",
            "/students",
        )

        # 9. Видалити першого створеного студента.
        send_request(
            "9. Видалити першого користувача (DELETE)",
            "DELETE",
            f"/students/{first_id}",
        )

        # 10. Отримати всіх наявних студентів після видалення.
        send_request(
            "10. Отримати всіх наявних студентів (GET)",
            "GET",
            "/students",
        )

    except requests.ConnectionError:
        message = (
            "ПОМИЛКА: не вдалося підключитися до REST API.\n"
            "Спочатку запустіть сервер командою: python app.py"
        )
        print(message)
        results.append(message)
    except requests.RequestException as error:
        message = f"ПОМИЛКА HTTP-запиту: {error}"
        print(message)
        results.append(message)
    except (KeyError, TypeError, ValueError) as error:
        message = f"ПОМИЛКА обробки відповіді сервера: {error}"
        print(message)
        results.append(message)
    finally:
        RESULTS_FILE.write_text("\n".join(results), encoding="utf-8")
        print(f"\nРезультати збережено у файл: {RESULTS_FILE.name}")


if __name__ == "__main__":
    main()
