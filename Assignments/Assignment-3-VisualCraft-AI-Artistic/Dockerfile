FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; exit(0 if urllib.request.urlopen('http://localhost:5001/health').getcode() == 200 else 1)"

CMD ["python", "service.py"]
