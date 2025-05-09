-- 集成系统管理平台数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE app;

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS user_projects;
DROP TABLE IF EXISTS project_platforms;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS platforms;

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建项目表
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建平台表
CREATE TABLE platforms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    url VARCHAR(256),
    internal_url VARCHAR(256),
    description TEXT,
    project_username VARCHAR(64),
    project_password VARCHAR(64),
    admin_username VARCHAR(64),
    admin_password VARCHAR(64),
    weight INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户与项目的关联表
CREATE TABLE user_projects (
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    PRIMARY KEY (user_id, project_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建项目与平台的关联表
CREATE TABLE project_platforms (
    project_id INT NOT NULL,
    platform_id INT NOT NULL,
    PRIMARY KEY (project_id, platform_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建默认管理员账户
-- 密码: admin123 (已使用Werkzeug的generate_password_hash函数生成哈希值)
INSERT INTO users (username, password_hash, is_admin)
VALUES ('admin', 'pbkdf2:sha256:600000$2Q4XOP38TJ0fbpVj$50bebe20325d7b0da51ae5edbc05344fba6f9db85a4d2c15810e3391b5324ebd', TRUE);

-- 添加示例数据（可选）
-- 添加示例项目
INSERT INTO projects (name, description) VALUES
('运维管理', '包含各种运维管理平台'),
('开发工具', '包含各种开发工具平台'),
('监控系统', '包含各种监控系统平台');

-- 添加示例平台
INSERT INTO platforms (name, url, internal_url, description, project_username, project_password, admin_username, admin_password, weight) VALUES
('Jenkins', 'https://jenkins.example.com', '192.168.1.10:8080', 'CI/CD自动化构建平台', 'dev_user', 'dev_pass', 'admin', 'admin_pass', 100),
('Grafana', 'https://grafana.example.com', '192.168.1.11:3000', '数据可视化监控平台', 'monitor_user', 'monitor_pass', 'admin', 'admin_pass', 90),
('GitLab', 'https://gitlab.example.com', '192.168.1.12:80', '代码仓库管理平台', 'git_user', 'git_pass', 'root', 'root_pass', 80),
('Prometheus', 'https://prometheus.example.com', '192.168.1.13:9090', '监控告警系统', 'prom_user', 'prom_pass', 'admin', 'admin_pass', 70),
('Kibana', 'https://kibana.example.com', '192.168.1.14:5601', '日志分析平台', 'kibana_user', 'kibana_pass', 'elastic', 'elastic_pass', 60);

-- 关联项目和平台
INSERT INTO project_platforms (project_id, platform_id) VALUES
(1, 1), -- 运维管理 - Jenkins
(1, 2), -- 运维管理 - Grafana
(2, 3), -- 开发工具 - GitLab
(3, 2), -- 监控系统 - Grafana
(3, 4), -- 监控系统 - Prometheus
(3, 5); -- 监控系统 - Kibana

-- 创建普通用户并关联项目
-- 密码: developer -> dev123, operator -> op123, monitor -> mon123
INSERT INTO users (username, password_hash, is_admin)
VALUES ('developer', 'pbkdf2:sha256:600000$KB7mmzzXEOVAFczx$7f0201b3574b55b3cc614abb7cee2483a220f5bf6143b176d5020e8546c7ab36', FALSE),
       ('operator', 'pbkdf2:sha256:600000$StSE1mRQmdPfGwfI$6aea858dadfc97217ec0279d74f81f63b21e531f37e56d787461e9234382443c', FALSE),
       ('monitor', 'pbkdf2:sha256:600000$ycHua0w5VzNFU2rv$6bf2dde0276ded64ec417e190f7fa2a292e9b920b00b33664dbfde8c319fe0aa', FALSE);

-- 关联用户和项目
INSERT INTO user_projects (user_id, project_id) VALUES
(2, 2), -- developer - 开发工具
(3, 1), -- operator - 运维管理
(4, 3); -- monitor - 监控系统
