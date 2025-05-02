FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser --disabled-password flaskuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
COPY start.sh .

RUN chmod +x start.sh
RUN chown -R flaskuser:flaskuser /app
USER flaskuser

ENTRYPOINT ["./start.sh"]
