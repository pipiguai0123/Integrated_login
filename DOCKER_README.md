# 集成系统管理平台 - Docker 部署指南

本文档提供了使用 Docker 部署集成系统管理平台的详细说明。

## 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)
- MySQL数据库服务器（已配置好的外部数据库）

## 数据库初始化

在启动应用程序之前，您需要先初始化数据库：

1. 使用提供的SQL脚本初始化数据库：

```bash
# 方法1：使用mysql命令行工具
mysql -h 164.155.64.10 -u root -p < init_db.sql

# 方法2：登录到MySQL后执行
mysql -h 164.155.64.10 -u root -p
# 输入密码后
source /path/to/init_db.sql
```

2. 验证数据库初始化是否成功：

```sql
USE app;
SHOW TABLES;
SELECT * FROM users;
```

更多关于数据库初始化的详细信息，请参阅 `DATABASE_README.md` 文件。

## 快速开始

1. 克隆代码库：

```bash
git clone <repository-url>
cd <repository-directory>
```

2. 使用 Docker Compose 构建并启动服务：

```bash
docker-compose up -d
```

3. 访问应用程序：

打开浏览器，访问 `http://localhost:5000`

默认管理员账户：
- 用户名：admin
- 密码：admin123

## 配置说明

### 环境变量

您可以通过修改 `docker-compose.yml` 文件中的环境变量来自定义应用程序的配置：

```yaml
environment:
  - TZ=Asia/Shanghai
  - DB_HOST=db
  - DB_USER=root
  - DB_PASSWORD=root123456789A
  - DB_PORT=3306
  - DB_NAME=app
  - DEBUG=False
```

### 数据持久化

应用程序使用 Docker 卷来持久化数据：

- `mysql-data`：MySQL 数据库文件
- `./flask_session:/app/flask_session`：Flask 会话文件

## 常用命令

### 启动服务

```bash
docker-compose up -d
```

### 查看日志

```bash
# 查看所有服务的日志
docker-compose logs

# 查看应用服务的日志
docker-compose logs app

# 查看数据库服务的日志
docker-compose logs db

# 实时查看日志
docker-compose logs -f
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 重建服务

如果您修改了 Dockerfile 或代码，需要重新构建镜像：

```bash
docker-compose build
docker-compose up -d
```

## 健康检查

应用程序提供了健康检查端点：

```
GET /health
```

响应示例：

```json
{
  "status": "healthy"
}
```

## 故障排除

### 数据库连接问题

如果应用程序无法连接到数据库，请检查：

1. 数据库服务是否正常运行：

```bash
docker-compose ps
```

2. 数据库连接信息是否正确：

```bash
docker-compose exec app env | grep DB_
```

3. 查看应用程序日志：

```bash
docker-compose logs app
```

### 容器无法启动

如果容器无法启动，请检查：

1. Docker 日志：

```bash
docker-compose logs
```

2. 确保端口未被占用：

```bash
netstat -tuln | grep 5000
netstat -tuln | grep 3306
```

## 生产环境部署

对于生产环境，建议：

1. 修改默认密码
2. 配置 HTTPS
3. 设置适当的资源限制
4. 配置外部数据库备份

## 更多信息

有关更多信息，请参阅项目的主 README 文件。
