from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request

from models.create_employee import Employee, EmployeeCreate

router = APIRouter(prefix="/employees", tags=["Сценарий 1: создание сотрудника"])


@router.post("", response_model=Employee, status_code=201)
def create_employee(data: EmployeeCreate, request: Request):
    employees = request.app.state.employees
    phones = {data.work_phone, data.mobile_phone}
    for employee in employees.values():
        if employee.email == data.email:
            raise HTTPException(409, "Email уже зарегистрирован")
        if phones & {employee.work_phone, employee.mobile_phone}:
            raise HTTPException(409, "Телефон уже зарегистрирован")

    employee = Employee(id=uuid4(), created_at=datetime.now(timezone.utc), **data.model_dump())
    employees[employee.id] = employee
    return employee


@router.get("", response_model=list[Employee])
def list_employees(request: Request):
    return list(request.app.state.employees.values())


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: UUID, request: Request):
    employee = request.app.state.employees.get(employee_id)
    if employee is None:
        raise HTTPException(404, "Сотрудник не найден")
    return employee
