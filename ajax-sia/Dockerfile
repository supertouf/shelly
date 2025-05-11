FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pysiaalarm paho-mqtt

CMD ["python", "receiver.py"]
