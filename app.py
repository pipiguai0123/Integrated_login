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

    # 健康检查端点
    @app.route('/health')
    def health():
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            return {'status': 'healthy'}, 200
        except Exception as e:
            app.logger.error(f'健康检查失败: {e}')
            return {'status': 'unhealthy', 'error': str(e)}, 500

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
