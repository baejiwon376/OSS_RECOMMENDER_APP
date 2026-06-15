FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY front/requirements.txt /app/front/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/front/requirements.txt

COPY front /app/front

EXPOSE 8501

CMD ["streamlit", "run", "front/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
