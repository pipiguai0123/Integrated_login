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
