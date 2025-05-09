FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    DB_HOST=db \
    DB_USER=root \
    DB_PASSWORD=root123456789A \
    DB_PORT=3306 \
    DB_NAME=app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    netcat-traditional \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 5000

# 复制启动脚本并设置权限
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 复制Docker专用配置文件
COPY config_docker.py /app/config.py

# 复制数据库初始化SQL脚本（仅供参考）
COPY init_db.sql /app/

# 设置启动命令
ENTRYPOINT ["docker-entrypoint.sh"]
