# 集成系统管理平台

这是一个基于Python Flask框架开发的集成系统管理平台，用于集中管理用户对不同平台的访问权限。

## 功能特点

### 管理员功能
- 用户管理（添加、编辑、删除用户）
- 项目管理（添加、编辑、删除项目）
- 平台管理（添加、编辑、删除平台）
- 用户-项目关联管理
- 项目-平台关联管理

### 普通用户功能
- 查看可访问的平台列表
- 跳转到相应平台

## 技术栈

- **后端框架**：Flask
- **数据库**：MySQL
- **ORM**：SQLAlchemy
- **认证**：Flask-Login
- **前端**：Bootstrap 5

## 系统架构

系统采用MVC架构设计：
- **模型(Model)**：定义数据库模型和业务逻辑
- **视图(View)**：HTML模板渲染页面
- **控制器(Controller)**：Flask路由处理请求

## 数据库设计

1. **users表** - 存储用户信息
   - id (主键)
   - username (用户名)
   - password_hash (密码，加密存储)
   - is_admin (是否为管理员)
   - created_at (创建时间)

2. **projects表** - 存储项目信息
   - id (主键)
   - name (项目名称)
   - description (项目描述)
   - created_at (创建时间)

3. **platforms表** - 存储平台信息
   - id (主键)
   - name (平台名称)
   - url (平台URL)
   - description (平台描述)
   - created_at (创建时间)

4. **user_projects表** - 用户与项目的关联表
   - user_id (外键，关联users表)
   - project_id (外键，关联projects表)

5. **project_platforms表** - 项目与平台的关联表
   - project_id (外键，关联projects表)
   - platform_id (外键，关联platforms表)

## 安装与部署

### 环境要求
- Python 3.8+
- MySQL 5.7+

### 安装步骤

1. **克隆代码库**
   ```
   git clone <repository-url>
   cd 集成系统管理
   ```

2. **安装依赖**
   ```
   pip install -r requirements.txt
   ```

3. **配置数据库**
   - 确保MySQL服务已启动
   - 创建名为`app`的数据库
   - 在`config.py`中配置数据库连接信息

4. **初始化数据库**
   - 系统首次启动时会自动创建所需的表
   - 同时会创建默认管理员账户（用户名：admin，密码：admin123）

5. **启动应用**
   ```
   python app.py
   ```

6. **访问系统**
   - 打开浏览器，访问 http://127.0.0.1:5000

## 使用指南

### 管理员操作流程

1. **登录系统**
   - 使用默认管理员账户登录：用户名 `admin`，密码 `admin123`
   - 登录后会自动跳转到管理员面板

2. **添加平台**
   - 在管理员面板中点击"平台管理"
   - 点击"添加平台"按钮
   - 填写平台名称、URL和描述
   - 点击"添加平台"按钮保存

3. **添加项目**
   - 在管理员面板中点击"项目管理"
   - 点击"添加项目"按钮
   - 填写项目名称和描述
   - 选择关联的平台
   - 点击"添加项目"按钮保存

4. **添加用户**
   - 在管理员面板中点击"用户管理"
   - 点击"添加用户"按钮
   - 填写用户名和密码
   - 选择是否具有管理员权限
   - 选择用户所属的项目
   - 点击"添加用户"按钮保存

### 普通用户操作流程

1. **登录系统**
   - 使用管理员创建的账户登录
   - 登录后会自动跳转到用户面板

2. **查看可访问平台**
   - 用户面板会显示所有可访问的平台列表

3. **访问平台**
   - 点击平台卡片上的"访问平台"按钮
   - 系统会自动跳转到相应平台的URL

## 项目结构

```
集成系统管理/
├── app.py                 # 应用程序入口
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── requirements.txt       # 项目依赖
├── routes/                # 路由目录
│   ├── __init__.py
│   ├── admin.py           # 管理员相关路由
│   ├── auth.py            # 认证相关路由
│   └── user.py            # 普通用户相关路由
├── static/                # 静态文件
│   ├── css/
│   │   └── style.css      # 自定义CSS
│   └── js/
│       └── main.js        # 自定义JavaScript
└── templates/             # HTML模板
    ├── base.html          # 基础模板
    ├── error.html         # 错误页面
    ├── login.html         # 登录页面
    ├── admin/             # 管理员页面
    │   ├── add_platform.html
    │   ├── add_project.html
    │   ├── add_user.html
    │   ├── dashboard.html
    │   ├── edit_platform.html
    │   ├── edit_project.html
    │   ├── edit_user.html
    │   ├── platforms.html
    │   ├── projects.html
    │   └── users.html
    └── user/              # 用户页面
        └── dashboard.html
```

## 代码详解

### 1. 配置文件 (config.py)

```python
import os

class Config:
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-integrated-management-system'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@192.168.18.145:3306/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 打印SQL语句，方便调试
    
    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 会话有效期（秒）
    
    # 调试配置
    DEBUG = True
```

### 2. 数据库模型 (models.py)

```python
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
        """获取用户可访问的所有平台"""
        platforms = []
        for project in self.projects:
            platforms.extend([p for p in project.platforms])
        # 去重
        return list(set(platforms))
    
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
    url = db.Column(db.String(256))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Platform {self.name}>'
```

### 3. 应用程序入口 (app.py)

```python
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth import auth
from routes.admin import admin
from routes.user import user
import os
import logging
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 初始化扩展
    db.init_app(app)
    
    # 设置登录管理器
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    
    # 添加上下文处理器，提供当前年份
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # 根路由重定向到登录页面
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.error(f'404错误: {e}')
        return render_template('error.html', error='404 页面未找到'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'500错误: {e}')
        return render_template('error.html', error='500 服务器内部错误'), 500
    
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('数据库表创建成功')
            
            # 检查是否存在管理员账户，如果不存在则创建一个默认管理员
            if not User.query.filter_by(is_admin=True).first():
                admin_user = User(username='admin', is_admin=True)
                admin_user.password = 'admin123'
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info('已创建默认管理员账户')
                print('已创建默认管理员账户')
        except Exception as e:
            app.logger.error(f'数据库初始化错误: {e}')
            print(f'数据库初始化错误: {e}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 4. 认证路由 (routes/auth.py)

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # 验证用户名和密码
        if user is None or not user.verify_password(password):
            flash('用户名或密码错误', 'danger')
            return render_template('login.html')
        
        # 登录用户
        login_user(user)
        
        # 获取next参数，即登录后要重定向的页面
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if user.is_admin:
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('user.dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))
```

### 5. 管理员路由 (routes/admin.py)

管理员路由包含了用户、项目和平台的管理功能，代码较长，这里展示部分关键代码：

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import User, Project, Platform, db

admin = Blueprint('admin', __name__, url_prefix='/admin')

# 管理员权限检查装饰器
def admin_required(func):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # 权限不足，返回403错误
        return func(*args, **kwargs)
    decorated_function.__name__ = func.__name__
    return login_required(decorated_function)

@admin.route('/')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

# 用户管理
@admin.route('/users')
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# 项目管理
@admin.route('/projects')
@admin_required
def projects():
    projects = Project.query.all()
    return render_template('admin/projects.html', projects=projects)

# 平台管理
@admin.route('/platforms')
@admin_required
def platforms():
    platforms = Platform.query.all()
    return render_template('admin/platforms.html', platforms=platforms)

# 其他管理功能...
```

### 6. 用户路由 (routes/user.py)

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import User, Platform, db

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/')
@login_required
def dashboard():
    # 获取用户可访问的平台
    platforms = current_user.get_accessible_platforms()
    return render_template('user/dashboard.html', platforms=platforms)

@user.route('/redirect/<int:platform_id>')
@login_required
def redirect_to_platform(platform_id):
    # 获取平台信息
    platform = Platform.query.get_or_404(platform_id)
    
    # 检查用户是否有权限访问该平台
    accessible_platforms = current_user.get_accessible_platforms()
    if platform not in accessible_platforms:
        abort(403)  # 权限不足，返回403错误
    
    # 重定向到平台URL
    return redirect(platform.url)
```

## 安全注意事项

1. 密码使用Werkzeug的`generate_password_hash`和`check_password_hash`进行加密和验证
2. 使用Flask-Login管理用户会话
3. 所有敏感操作都有权限验证
4. 防止未授权访问的路由保护

## 常见问题解答

1. **Q: 如何修改默认管理员账户？**
   A: 登录后在用户管理中修改admin用户的信息，或直接在数据库中修改。

2. **Q: 如何备份数据库？**
   A: 使用MySQL的备份工具，如mysqldump：
   ```
   mysqldump -u root -p app > backup.sql
   ```

3. **Q: 如何在生产环境中部署？**
   A: 建议使用Gunicorn或uWSGI作为WSGI服务器，Nginx作为反向代理。

4. **Q: 忘记管理员密码怎么办？**
   A: 可以通过直接操作数据库重置密码，或编写一个密码重置脚本。

## 维护与更新

- 定期更新依赖包以修复安全漏洞
- 备份数据库以防数据丢失
- 监控系统日志以发现潜在问题

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请联系项目维护者。
