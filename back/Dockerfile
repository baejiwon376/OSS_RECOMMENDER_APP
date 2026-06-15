FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY back/requirements.txt /app/back/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/back/requirements.txt

COPY back /app/back
COPY data /app/data

EXPOSE 8000

CMD ["uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
