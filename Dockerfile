FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt

COPY app app

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"]
