FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
COPY . .
RUN chmod +x wait-for-db.sh start-server.sh
CMD ["./wait-for-db.sh", "db", "5432", "sh", "-c", "gunicorn --bind 0.0.0.0:8080 foodgram.wsgi"]
