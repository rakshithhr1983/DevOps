FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persistent volume directory for user database
RUN mkdir -p /data

EXPOSE 5000

CMD ["python", "app.py"]
