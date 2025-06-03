FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY netatmo_to_mqtt.py .

CMD ["python", "netatmo_to_mqtt.py"]
