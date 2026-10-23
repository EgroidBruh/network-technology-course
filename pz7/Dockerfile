FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd --create-home appuser
COPY planner ./planner
USER appuser

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "planner.main:app", "--host", "0.0.0.0", "--port", "8080"]
