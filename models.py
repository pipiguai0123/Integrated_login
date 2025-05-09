from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# 用户与项目的关联表
user_projects = db.Table('user_projects',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
)

# 项目与平台的关联表
project_platforms = db.Table('project_platforms',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('platform_id', db.Integer, db.ForeignKey('platforms.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 用户所属的项目（多对多关系）
    projects = db.relationship('Project', secondary=user_projects,
                              backref=db.backref('users', lazy='dynamic'),
                              lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_accessible_platforms(self):
        """获取用户可访问的所有平台，按权重排序"""
        platforms = []
        for project in self.projects:
            platforms.extend([p for p in project.platforms])
        # 去重
        unique_platforms = list(set(platforms))
        # 按权重降序排序，权重相同时按名称升序排序
        return sorted(unique_platforms, key=lambda p: (-p.weight, p.name))

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 项目关联的平台（多对多关系）
    platforms = db.relationship('Platform', secondary=project_platforms,
                               backref=db.backref('projects', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class Platform(db.Model):
    __tablename__ = 'platforms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    url = db.Column(db.String(256))  # 外网URL，用于直接访问
    internal_url = db.Column(db.String(256))  # 内网URL，用于代理访问
    description = db.Column(db.Text)
    # 平台登录账号信息
    project_username = db.Column(db.String(64))  # 项目账号用户名
    project_password = db.Column(db.String(64))  # 项目账号密码
    admin_username = db.Column(db.String(64))    # 超管账号用户名
    admin_password = db.Column(db.String(64))    # 超管账号密码
    weight = db.Column(db.Integer, default=0)    # 权重，用于排序，数值越大越靠前
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_proxy_url(self, use_internal=False):
        """
        获取用于访问的URL

        参数:
            use_internal (bool): 是否优先使用内网URL
                - True: 优先使用内网URL（适用于服务器内部访问）
                - False: 优先使用外网URL（适用于外部浏览器访问）
        """
        # 如果指定使用内网URL且内网URL存在
        if use_internal and self.internal_url and self.internal_url.strip():
            return self.internal_url

        # 如果外网URL存在，使用外网URL
        elif self.url and self.url.strip():
            return self.url

        # 如果外网URL不存在但内网URL存在，使用内网URL（即使指定了不使用内网URL）
        elif self.internal_url and self.internal_url.strip():
            return self.internal_url

        # 如果两者都不存在，返回空字符串
        else:
            return ""

    def has_login_info(self):
        """检查是否配置了登录信息"""
        return bool(self.project_username or self.admin_username)

    def __repr__(self):
        return f'<Platform {self.name}>'
