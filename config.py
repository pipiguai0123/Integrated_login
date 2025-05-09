import os

class Config:
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-integrated-management-system'

    # 数据库配置
    # 数据库连接字符串
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123456789A@164.155.64.10:3306/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 打印SQL语句，方便调试

    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 会话有效期（秒）

    # 调试配置
    DEBUG = True
