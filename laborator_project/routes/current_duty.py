import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from models import CurrentDuty, DefaultDuty, Role, Shift, ShiftCreate

router = APIRouter(prefix="/duty", tags=["Сценарий 2: текущий дежурный"])
logger = logging.getLogger("uvicorn.error")


@router.post("/shifts", response_model=Shift, status_code=201)
def create_shift(data: ShiftCreate, request: Request):
    state = request.app.state
    if data.employee_id not in state.employees:
        raise HTTPException(404, "Сотрудник не найден")
    for shift in state.shifts.values():
        if data.start_time <= shift.end_time and data.end_time >= shift.start_time:
            raise HTTPException(409, "Смена пересекается с существующей")
    shift = Shift(id=uuid4(), **data.model_dump())
    state.shifts[shift.id] = shift
    return shift


@router.get("/shifts", response_model=list[Shift])
def list_shifts(request: Request):
    return list(request.app.state.shifts.values())


@router.put("/default", response_model=DefaultDuty)
def set_default_duty(data: DefaultDuty, request: Request):
    employee = request.app.state.employees.get(data.employee_id)
    if employee is None:
        raise HTTPException(404, "Сотрудник не найден")
    if employee.role != Role.SHIFT_LEAD:
        raise HTTPException(422, "Дежурный по умолчанию должен быть старшим смены (SHIFT_LEAD)")
    request.app.state.default_duty_id = employee.id
    return data


@router.get("/current", response_model=CurrentDuty)
def get_current_duty(request: Request):
    state = request.app.state
    now = datetime.now(timezone.utc)
    shift = next((s for s in state.shifts.values() if s.start_time <= now <= s.end_time), None)
    source = "schedule"
    if shift is not None:
        employee = state.employees[shift.employee_id]
    else:
        logger.warning("Текущий дежурный не назначен; выбираем старшего смены")
        employee = state.employees.get(state.default_duty_id)
        source = "default"

    if employee is None:
        logger.error("Не назначен ни текущий, ни резервный дежурный")
        raise HTTPException(503, "Не найден ответственный специалист")
    return CurrentDuty(
        employee_id=employee.id,
        name=" ".join(filter(None, [employee.last_name, employee.first_name, employee.middle_name])),
        phone_number=employee.mobile_phone,
        source=source,
        resolved_at=now,
    )
