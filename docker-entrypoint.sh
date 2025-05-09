#!/bin/bash
set -e

# 检查MySQL连接
echo "Checking MySQL connection..."
for i in {1..30}; do
  if python -c "import pymysql; pymysql.connect(host='$DB_HOST', user='$DB_USER', password='$DB_PASSWORD', port=int('$DB_PORT'), database='$DB_NAME')" 2>/dev/null; then
    echo "MySQL connection successful!"
    break
  fi

  echo "Attempt $i: Cannot connect to MySQL yet, retrying in 2 seconds..."
  sleep 2

  if [ $i -eq 30 ]; then
    echo "Could not connect to MySQL after 30 attempts. Please check your database configuration."
    exit 1
  fi
done

# 启动应用
echo "Starting application..."
exec python app.py
