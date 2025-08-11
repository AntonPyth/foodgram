#!/bin/sh
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "⏳ Ожидание базы данных на ${host}:${port}..."
until nc -z "$host" "$port"; do
  sleep 1
done

echo "✅ База данных доступна, запускаем: $cmd"
exec $cmd