# Практическая работа №8 — подключение к реляционной базе данных

Планировщик событий на FastAPI, SQLite и SQLModel по заданию
[ПЗ №8](ПЗ№8_Подключение%20к%20реляционной%20базе%20данных.pdf).
Вместо коллекций в памяти используются таблицы `events` и `users`.
Реализованы создание, чтение, частичное обновление и удаление событий,
регистрация и проверка входа. Данные сохраняются после перезапуска.

## Запуск в Docker

Из каталога проекта:

```bash
mkdir -p data
LOCAL_UID="$(id -u)" LOCAL_GID="$(id -g)" docker compose up --build -d
```

Откройте **http://localhost:8081/docs** — Swagger UI для всех операций.
Корневой адрес `/` перенаправляет в документацию.

```bash
docker compose ps
docker compose logs -f planner
docker compose down
```

SQLite хранится в файле `./data/planner.db` на компьютере; каталог `./data`
подключён в контейнер как `/app/data` (bind mount). Остановка, пересоздание
контейнера и `docker compose down -v` не удаляют этот каталог.
Compose запускает приложение с UID/GID пользователя компьютера, чтобы
приложение и SQLite Browser могли работать с одним файлом. По умолчанию
используются UID/GID 1000; команда запуска выше подставляет фактические значения.
Внутри контейнера приложение слушает порт 8080,
проверка здоровья выполняет запрос к БД через `GET /event/`.
Для первой сборки нужен интернет. Если порт занят, измените левый порт
в `compose.yaml`, например на `127.0.0.1:8082:8080`.

Запуск без Compose:

```bash
docker build -t pz8-planner .
mkdir -p data
docker run --rm -d --name pz8-planner \
  -p 127.0.0.1:8081:8080 \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$(pwd)/data,target=/app/data" pz8-planner
```

Эти команды предназначены для запуска пользователем. При подготовке работы
Docker-сокет не использовался; сборка и запуск контейнера не выполнялись.

## Просмотр БД в SQLite Browser

```bash
sqlitebrowser ./data/planner.db
```

Во вкладке Browse Data выберите `events` или `users`. После запроса через API
нажмите обновление данных или заново откройте БД. Не оставляйте в просмотрщике
незавершённую транзакцию редактирования: она может блокировать запись из API.

Если приложение уже запускалось с прежним именованным томом, **до пересоздания
контейнера** перенесите существующую БД:

```bash
mkdir -p data
docker compose stop planner
docker compose cp planner:/app/data/planner.db ./data/planner.db
LOCAL_UID="$(id -u)" LOCAL_GID="$(id -g)" docker compose up -d --force-recreate
```

Копируйте только если нужно сохранить прежнюю БД; команда заменяет файл
`./data/planner.db`, если он уже существует. Старый том автоматически не удаляется.

## Маршруты

| Метод | Путь | Результат |
| --- | --- | --- |
| POST | `/user/signup` | Регистрация; повторный email — 409 |
| POST | `/user/signin` | Проверка входа; неизвестный email — 404, неверный пароль — 403 |
| POST | `/event/new` | Создание; ответ содержит `message` и `id` |
| GET | `/event/` | Все события в порядке ID |
| GET | `/event/{id}` | Одно событие; отсутствующее — 404 |
| PUT | `/event/edit/{id}` | Изменение переданных полей; отсутствующее — 404 |
| DELETE | `/event/delete/{id}` | Удаление одного события; отсутствующее — 404 |
| DELETE | `/event/` | Удаление всех событий |

Успешные операции возвращают 200. Ошибки валидации — 422.
Старые пути `PUT /event/{id}` и `DELETE /event/{id}` также работают.

## Два набора команд

Запустите приложение и выполните из другого терминала:

```bash
# Набор 1: создание → список → чтение → обновление → удаление → 404.
BASE_URL=http://localhost:8081 bash scripts/demo-crud.sh

# Набор 2: регистрация, повторная регистрация, вход и ошибки 403/404/422.
BASE_URL=http://localhost:8081 bash scripts/demo-errors.sh
```

Скрипты содержат команды curl, проверяют ожидаемые коды ответа и завершаются
с ненулевым кодом при ошибке. Нужны bash, curl и python3 (для чтения ID и UUID).
Первый скрипт удаляет только созданное им событие; второй оставляет учебного
пользователя с уникальным email. Можно запускать повторно.
Для другого адреса: `BASE_URL=http://localhost:8081 bash scripts/demo-crud.sh`.

Пример создания (поле `id` можно не передавать — его назначит SQLite):

```bash
curl -i -X POST http://localhost:8081/event/new \
  -H 'Content-Type: application/json' \
  -d '{"title":"Семинар SQLite","image":"sqlite.png","description":"Практика SQLModel","tags":["sqlite","python"],"location":"Аудитория 101"}'
```

Ответ: `{"message":"Event created successfully","id":1}` (ID может отличаться).
Подставьте полученный ID в следующие команды:

```bash
curl http://localhost:8081/event/1
curl -X PUT http://localhost:8081/event/edit/1 \
  -H 'Content-Type: application/json' -d '{"location":"Hybrid"}'
curl -X DELETE http://localhost:8081/event/delete/1
```

При обновлении неуказанные поля сохраняются. Пустой объект `{}` не меняет запись;
`null`, пустой заголовок, пустая локация и неизвестные поля возвращают 422.
Список тегов можно очистить через `{"tags":[]}`.
Для совместимости допускается явный положительный `id` при создании;
повторный ID возвращает 409, изменение ID запрещено.

## Проверка сохранения в Docker

Создайте событие и пользователя через Swagger UI. Запишите ID события.
Выполните:

```bash
docker compose down
docker compose up -d
```

Снова получите событие и выполните вход с прежними данными.
Оба запроса должны завершиться 200. Для просмотра схемы БД:

```bash
docker compose exec planner python -c 'import sqlite3; db=sqlite3.connect("/app/data/planner.db"); print(*db.execute("SELECT sql FROM sqlite_master WHERE type = ?", ("table",)), sep="\n")'
```

## Устройство приложения

```text
planner/
├── main.py                 # фабрика приложения, lifespan, маршруты
├── security.py             # хеширование паролей scrypt
├── database/connection.py  # engine, создание таблиц, сессии
├── models/events.py        # Event, EventCreate, EventRead, EventUpdate
├── models/users.py         # схемы пользователя и таблица UserRecord
└── routes/                 # HTTP-операции событий и пользователей
scripts/demo-crud.sh         # первый набор команд
scripts/demo-errors.sh       # второй набор команд
tests/test_api.py            # API, схема и сохранение в SQLite
docs/report.md              # отчёт по практической работе
docs/use-cases.md           # варианты использования
Dockerfile
compose.yaml
```

`DATABASE_URL` задаёт расположение БД (по умолчанию локально
`sqlite:///./data/planner.db`, в Docker — `sqlite:////app/data/planner.db`).
Каталог и таблицы создаются при запуске через lifespan и `create_all`.
`SQL_ECHO=true` включает журнал SQL. Каждый запрос получает свою `Session`
через `Depends(get_session)`; изменения фиксируются `commit`, данные
обновляются через `refresh`. Модели запроса отделены от ORM-таблиц, поэтому
входные данные проходят валидацию до записи.

Пароли сохраняются как хеши scrypt с индивидуальной солью. Вход только проверяет
данные: токены, сессии и ограничение доступа к событиям не реализованы.
Поле `User.events` сохраняется как JSON-снимок переданного списка событий;
оно не является связью с таблицей `events` и автоматически не обновляется.
Основная сущность индивидуальной темы — событие планировщика.
MongoDB не используется: итоговые задания ПЗ №8 требуют SQLite и SQLModel.

## Локальная проверка без Docker

Python 3.10+; образ использует Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m uvicorn planner.main:app --host 127.0.0.1 --port 8080 --reload
```

Тесты используют отдельные временные файлы SQLite и не затрагивают рабочую БД.
Проверка перезапуска создаёт независимые экземпляры приложения с одним файлом
и проверяет сохранение создания, обновления, удаления и пользователей.
Подробности выполнения и результаты приведены в [отчёте](docs/report.md).
