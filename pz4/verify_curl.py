"""Проверка запущенного локального API через curl; очищает список задач."""

import json
from pathlib import Path
import shlex
import subprocess
import sys


BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
RESULTS = Path(__file__).resolve().parent / "results"


def main():
    RESULTS.mkdir(exist_ok=True)
    cases = []
    transcript = []

    def check(title, method, path, expected_status, payload=None, expected=None):
        command = ["curl", "--silent", "--show-error", "--max-time", "10",
                   "--include", "-X", method, BASE_URL + path,
                   "-H", "accept: application/json"]
        if payload is not None:
            command += ["-H", "Content-Type: application/json", "-d",
                        json.dumps(payload, ensure_ascii=False)]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        headers, body = result.stdout.split("\n\n", 1)
        actual_status = int(headers.splitlines()[0].split()[1])
        data = json.loads(body)
        assert actual_status == expected_status, (title, actual_status, body)
        if expected is not None:
            assert data == expected, (title, data, expected)
        entry = {"title": title, "command": shlex.join(command),
                 "status": actual_status, "response": data,
                 "raw_response": result.stdout}
        cases.append(entry)
        transcript.append(f"### {title}\n$ {entry['command']}\n{result.stdout}\n")
        print(f"OK {actual_status}: {title}")
        return data

    check("Приветствие", "GET", "/", 200,
          expected={"message": "Добро пожаловать в приложение Егора!"})
    check("Очистка перед проверкой", "DELETE", "/todo", 200,
          expected={"message": "Егор, все задачи успешно удалены!"})
    check("Пустой список", "GET", "/todo", 200, expected={"todos": []})
    check("Создание задачи", "POST", "/todo", 201,
          {"id": 1, "item": "Изучить модели ответов FastAPI"},
          {"message": "Егор, задача успешно добавлена!"})
    check("Список без ID", "GET", "/todo", 200,
          expected={"todos": [{"item": "Изучить модели ответов FastAPI"}]})
    check("Одна задача с ID", "GET", "/todo/1", 200,
          expected={"todo": {"id": 1, "item": "Изучить модели ответов FastAPI"}})
    check("Обновление задачи", "PUT", "/todo/1", 200,
          {"item": "Подготовить отчёт по практической работе"},
          {"message": "Егор, задача успешно обновлена!"})
    updated = {"id": 1, "item": "Подготовить отчёт по практической работе"}
    check("Проверка обновлённого текста и сохранения ID", "GET", "/todo/1", 200,
          expected={"todo": updated})
    check("Повторный ID", "POST", "/todo", 409,
          {"id": 1, "item": "Дубликат"},
          {"detail": "Егор, задача с указанным ID уже существует."})
    check("Дубликат не изменил список", "GET", "/todo", 200,
          expected={"todos": [{"item": updated["item"]}]})
    check("Удаление одной задачи", "DELETE", "/todo/1", 200,
          expected={"message": "Егор, задача успешно удалена!"})
    for method, title, payload in [
        ("GET", "Получение отсутствующей задачи", None),
        ("PUT", "Обновление отсутствующей задачи", {"item": "Новый текст"}),
        ("DELETE", "Удаление отсутствующей задачи", None),
    ]:
        check(title, method, "/todo/1", 404, payload,
              {"detail": "Егор, задача с указанным ID не найдена."})
    check("Создание первой задачи для общей очистки", "POST", "/todo", 201,
          {"id": 2, "item": "Изучить HTTPException"})
    check("Создание второй задачи для общей очистки", "POST", "/todo", 201,
          {"id": 3, "item": "Проверить API через curl"})
    check("Две задачи без ID", "GET", "/todo", 200,
          expected={"todos": [{"item": "Изучить HTTPException"},
                              {"item": "Проверить API через curl"}]})
    check("Удаление всех задач", "DELETE", "/todo", 200,
          expected={"message": "Егор, все задачи успешно удалены!"})
    check("Список после удаления всех задач", "GET", "/todo", 200,
          expected={"todos": []})
    error = check("Неверный тип ID в пути", "GET", "/todo/not-a-number", 422)
    assert error["detail"][0]["loc"] == ["path", "todo_id"]
    error = check("Нет обязательного поля item при создании", "POST", "/todo", 422,
                  {"id": 4})
    assert error["detail"][0]["loc"] == ["body", "item"]
    error = check("Нет обязательного поля item при обновлении", "PUT", "/todo/4", 422, {})
    assert error["detail"][0]["loc"] == ["body", "item"]
    check("Ошибочные запросы не добавили задачи", "GET", "/todo", 200,
          expected={"todos": []})
    schema = subprocess.run(
        ["curl", "--silent", "--show-error", "--max-time", "10",
         BASE_URL + "/openapi.json"], capture_output=True, text=True, check=True)
    openapi = json.loads(schema.stdout)
    assert openapi["paths"]["/todo"]["get"]["responses"]["200"]["content"][
        "application/json"]["schema"]["$ref"].endswith("/TodoItems")
    assert "201" in openapi["paths"]["/todo"]["post"]["responses"]
    assert "example" in openapi["components"]["schemas"]["TodoItem"]
    (RESULTS / "openapi.json").write_text(schema.stdout + "\n", encoding="utf-8")
    (RESULTS / "curl-results.json").write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "curl-transcript.txt").write_text("\n".join(transcript), encoding="utf-8")
    print(f"Проверено запросов curl: {len(cases)}; схема OpenAPI проверена.")


if __name__ == "__main__":
    main()
