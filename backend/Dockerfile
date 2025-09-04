FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
RUN chmod +x wait-for-db.sh start-server.sh
RUN useradd -m appuser
USER appuser
CMD ["./wait-for-db.sh", "db", "5432", "./start-server.sh"]
ENV PYTHONPATH=/app
