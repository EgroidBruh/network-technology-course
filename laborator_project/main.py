from fastapi import FastAPI

from routes.create_employee import router as employees_router
from routes.current_duty import router as duty_router
from routes.register_incident import router as incidents_router

app = FastAPI(title="Сервис дежурств — MVP", version="0.1.0")

# Временные данные одного процесса. При перезапуске всё очищается.
app.state.employees = {}
app.state.shifts = {}
app.state.default_duty_id = None
app.state.incidents = {}
app.state.incident_events = {}

app.include_router(employees_router)
app.include_router(duty_router)
app.include_router(incidents_router)
