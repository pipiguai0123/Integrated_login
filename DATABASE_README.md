# 集成系统管理平台 - 数据库初始化指南

本文档提供了如何使用SQL脚本初始化数据库的详细说明。

## 数据库初始化步骤

### 1. 准备MySQL环境

确保您已经安装并启动了MySQL服务器。您可以使用以下命令检查MySQL服务是否正在运行：

```bash
# Windows
sc query mysql

# Linux
systemctl status mysql
```

### 2. 执行SQL初始化脚本

您可以使用以下命令执行SQL初始化脚本：

```bash
# 方法1：使用mysql命令行工具
mysql -h 164.155.64.10 -u root -p < init_db.sql

# 方法2：登录到MySQL后执行
mysql -h 164.155.64.10 -u root -p
# 输入密码后
source /path/to/init_db.sql
```

### 3. 验证数据库初始化

执行以下SQL查询，验证数据库是否成功初始化：

```sql
USE app;
SHOW TABLES;
SELECT * FROM users;
```

您应该能看到以下表：
- users
- projects
- platforms
- user_projects
- project_platforms

并且users表中应该有一个管理员账户和三个普通用户账户。

## 数据库结构说明

### 用户表 (users)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(64) | 用户名，唯一 |
| password_hash | VARCHAR(128) | 密码哈希值 |
| is_admin | BOOLEAN | 是否为管理员 |
| created_at | DATETIME | 创建时间 |

### 项目表 (projects)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(64) | 项目名称，唯一 |
| description | TEXT | 项目描述 |
| created_at | DATETIME | 创建时间 |

### 平台表 (platforms)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(64) | 平台名称，唯一 |
| url | VARCHAR(256) | 外网URL |
| internal_url | VARCHAR(256) | 内网URL |
| description | TEXT | 平台描述 |
| project_username | VARCHAR(64) | 项目账号用户名 |
| project_password | VARCHAR(64) | 项目账号密码 |
| admin_username | VARCHAR(64) | 超管账号用户名 |
| admin_password | VARCHAR(64) | 超管账号密码 |
| weight | INT | 权重，用于排序 |
| created_at | DATETIME | 创建时间 |

### 用户与项目关联表 (user_projects)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | INT | 用户ID，外键 |
| project_id | INT | 项目ID，外键 |

### 项目与平台关联表 (project_platforms)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| project_id | INT | 项目ID，外键 |
| platform_id | INT | 平台ID，外键 |

## 默认账户信息

### 管理员账户
- 用户名：admin
- 密码：admin123

### 普通用户账户
- 开发者：developer / dev123
- 运维：operator / op123
- 监控：monitor / mon123
