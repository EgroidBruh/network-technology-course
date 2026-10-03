FROM python:3.11-slim
WORKDIR /opt/app
RUN pip install fastapi uvicorn
EXPOSE 8000
COPY ./api.py .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
