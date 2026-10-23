# Практическая работа №7 — планировщик событий

Приложение по методичке `PZ_6_Strukturirovanie_prilozheniy_FastAPI.pdf`
(внутри документа — занятие №7). Исходный список задач и HTML-шаблоны заменены
модульным API пользователей и событий.

## Запуск в Docker

Выполните из каталога проекта:

```bash
docker build -t pz7-planner .
docker run --rm -d --name pz7-planner -p 127.0.0.1:8080:8080 pz7-planner
```

Откройте <http://localhost:8080/docs>. В Swagger UI выберите метод, нажмите
**Try it out**, заполните данные и нажмите **Execute**. Корневой адрес `/`
также перенаправляет в документацию. Схема API: <http://localhost:8080/openapi.json>.

Просмотр логов и остановка:

```bash
docker logs -f pz7-planner
docker stop pz7-planner
```

Для первой сборки нужен интернет. В контейнере приложение слушает порт 8080
и работает от непривилегированного пользователя. Если порт компьютера занят,
укажите `-p 127.0.0.1:8081:8080` и откройте <http://localhost:8081/docs>.

## Структура и модели

```text
planner/
├── __init__.py
├── main.py                 # приложение и подключение маршрутов
├── database/
│   ├── __init__.py
│   └── connection.py       # заготовка для следующей работы
├── models/
│   ├── __init__.py
│   ├── events.py           # Event
│   └── users.py            # User, NewUser, UserSignIn
└── routes/
    ├── __init__.py
    ├── events.py           # операции с событиями
    └── users.py            # регистрация и вход
docs/use-cases.md           # диаграмма и основные сценарии
tests/test_api.py           # проверки API
Dockerfile
requirements.txt
requirements-dev.txt
```

`User` содержит email и список событий, по умолчанию пустой. `NewUser` наследует
`User` и добавляет пароль; `UserSignIn` содержит email и пароль для входа.
`Event` содержит `id`, `title`, `image`, `description`, `tags`, `location`.
Email проверяется Pydantic; положительный уникальный ID события задаёт клиент.
Примеры моделей доступны в Swagger UI.

## Маршруты

| Метод | Путь | Назначение |
| --- | --- | --- |
| POST | `/user/signup` | Регистрация; повторный email — 409 |
| POST | `/user/signin` | Вход; неизвестный email — 404, неверный пароль — 403 |
| GET | `/event/` | Список всех событий |
| GET | `/event/{id}` | Событие по ID; неизвестный ID — 404 |
| POST | `/event/new` | Создание; повторный ID — 409 |
| DELETE | `/event/{id}` | Удаление одного события; неизвестный ID — 404 |
| DELETE | `/event/` | Удаление всех событий |

Некорректные данные возвращают 422. Успешные операции возвращают 200, как в методичке.

## Примеры curl

Регистрация и вход:

```bash
curl -i -X POST http://localhost:8080/user/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"fastapi@packt.com","password":"Stro0ng!"}'

curl -i -X POST http://localhost:8080/user/signin \
  -H 'Content-Type: application/json' \
  -d '{"email":"fastapi@packt.com","password":"Stro0ng!"}'
```

Создание и просмотр события:

```bash
curl -i -X POST http://localhost:8080/event/new \
  -H 'Content-Type: application/json' \
  -d '{"id":1,"title":"FastAPI Book Launch","image":"https://linktomyimage.com/image.png","description":"Обсуждение книги FastAPI","tags":["python","fastapi","book","launch"],"location":"Google Meet"}'

curl -i http://localhost:8080/event/
curl -i http://localhost:8080/event/1
```

Удаление:

```bash
curl -i -X DELETE http://localhost:8080/event/1
curl -i -X DELETE http://localhost:8080/event/1
curl -i -X DELETE http://localhost:8080/event/
```

Первое удаление возвращает 200, повторное — 404. После очистки списка
`GET /event/` возвращает `[]`.

## Границы текущей работы

Как в примерах методички, пользователи хранятся в словаре, события — в списке
в памяти. При перезапуске все данные исчезают. Используется один процесс Uvicorn.
Подключение БД и обновление событий отложены до следующей работы.

Вход проверяет email и пароль и возвращает сообщение. Токены, сессии, выход
и ограничение доступа к событиям пока не реализованы. Операции с событиями доступны
любому клиенту. Список `User.events` автоматически не связывается с создаваемыми
событиями. Пароли хранятся в памяти в открытом виде по учебному примеру;
это не подходит для рабочего сервиса.

Исправлены опечатки методички: согласованы имена модулей и импорты, существование
пользователя проверяется до обращения к словарю, примеры схем адаптированы
к Pydantic 2. Дополнительно отклоняются события с повторным ID.
Задание 3 выполнено в [диаграмме и сценариях](docs/use-cases.md).

## Локальный запуск и тесты

Нужен Python 3.10 или новее; Docker использует Python 3.12.
Выполните из корня проекта:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m uvicorn planner.main:app --host 127.0.0.1 --port 8080 --reload
```

Другой вариант запуска: `python -m planner.main`.
В Windows для активации окружения в cmd используйте `.venv\Scripts\activate`.
