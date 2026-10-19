FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home app
COPY main.py models.py ./
COPY routes routes
USER app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
