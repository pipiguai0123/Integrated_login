import os

class Config:
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-integrated-management-system'

    # 数据库配置
    # 使用环境变量或默认值
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root123456789A')
    DB_HOST = os.environ.get('DB_HOST', 'db')  # 使用docker-compose中的服务名
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'app')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'

    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME', '3600'))  # 会话有效期（秒）

    # 调试配置
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
