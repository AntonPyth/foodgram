#!/bin/sh
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "⏳ Ожидание базы данных на ${host}:${port}..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U $POSTGRES_USER -d $POSTGRES_DB -c '\q' > /dev/null 2>&1; do
  sleep 1
done

echo "✅ База данных доступна, запускаем: $cmd"
exec $cmd