#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
用于从零创建数据库结构，包含所有最新的字段
"""

from app import create_app
from models import db, User, Project, Platform
import logging

def init_db():
    """初始化数据库，创建所有表和默认管理员账户"""
    app = create_app()
    with app.app_context():
        try:
            # 删除所有现有表（如果存在）
            db.drop_all()
            print("已删除所有现有表")
            
            # 创建所有表
            db.create_all()
            print("已创建所有表")
            
            # 创建默认管理员账户
            if not User.query.filter_by(is_admin=True).first():
                admin_user = User(username='admin', is_admin=True)
                admin_user.password = 'admin123'
                db.session.add(admin_user)
                db.session.commit()
                print("已创建默认管理员账户: 用户名=admin, 密码=admin123")
            
            print("数据库初始化完成！")
            
        except Exception as e:
            logging.error(f"数据库初始化错误: {e}")
            print(f"数据库初始化错误: {e}")
            db.session.rollback()

if __name__ == "__main__":
    init_db()
