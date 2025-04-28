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

@admin.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = True if request.form.get('is_admin') else False
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # 创建新用户
        user = User(username=username, is_admin=is_admin)
        user.password = password
        
        # 添加用户到项目
        project_ids = request.form.getlist('projects')
        for project_id in project_ids:
            project = Project.query.get(project_id)
            if project:
                user.projects.append(project)
        
        db.session.add(user)
        db.session.commit()
        
        flash('用户添加成功', 'success')
        return redirect(url_for('admin.users'))
    
    projects = Project.query.all()
    return render_template('admin/add_user.html', projects=projects)

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = True if request.form.get('is_admin') else False
        
        # 检查用户名是否已被其他用户使用
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin.edit_user', id=id))
        
        # 更新用户信息
        user.username = username
        if password:
            user.password = password
        user.is_admin = is_admin
        
        # 更新用户项目关联
        user.projects = []
        project_ids = request.form.getlist('projects')
        for project_id in project_ids:
            project = Project.query.get(project_id)
            if project:
                user.projects.append(project)
        
        db.session.commit()
        
        flash('用户更新成功', 'success')
        return redirect(url_for('admin.users'))
    
    projects = Project.query.all()
    user_projects = [p.id for p in user.projects]
    return render_template('admin/edit_user.html', user=user, projects=projects, user_projects=user_projects)

@admin.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # 不允许删除当前登录的用户
    if user.id == current_user.id:
        flash('不能删除当前登录的用户', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('用户删除成功', 'success')
    return redirect(url_for('admin.users'))

# 项目管理
@admin.route('/projects')
@admin_required
def projects():
    projects = Project.query.all()
    return render_template('admin/projects.html', projects=projects)

@admin.route('/projects/add', methods=['GET', 'POST'])
@admin_required
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 检查项目名是否已存在
        if Project.query.filter_by(name=name).first():
            flash('项目名已存在', 'danger')
            return redirect(url_for('admin.add_project'))
        
        # 创建新项目
        project = Project(name=name, description=description)
        
        # 添加项目关联的平台
        platform_ids = request.form.getlist('platforms')
        for platform_id in platform_ids:
            platform = Platform.query.get(platform_id)
            if platform:
                project.platforms.append(platform)
        
        db.session.add(project)
        db.session.commit()
        
        flash('项目添加成功', 'success')
        return redirect(url_for('admin.projects'))
    
    platforms = Platform.query.all()
    return render_template('admin/add_project.html', platforms=platforms)

@admin.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 检查项目名是否已被其他项目使用
        existing_project = Project.query.filter_by(name=name).first()
        if existing_project and existing_project.id != project.id:
            flash('项目名已存在', 'danger')
            return redirect(url_for('admin.edit_project', id=id))
        
        # 更新项目信息
        project.name = name
        project.description = description
        
        # 更新项目平台关联
        project.platforms = []
        platform_ids = request.form.getlist('platforms')
        for platform_id in platform_ids:
            platform = Platform.query.get(platform_id)
            if platform:
                project.platforms.append(platform)
        
        db.session.commit()
        
        flash('项目更新成功', 'success')
        return redirect(url_for('admin.projects'))
    
    platforms = Platform.query.all()
    project_platforms = [p.id for p in project.platforms]
    return render_template('admin/edit_project.html', project=project, platforms=platforms, project_platforms=project_platforms)

@admin.route('/projects/delete/<int:id>', methods=['POST'])
@admin_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('项目删除成功', 'success')
    return redirect(url_for('admin.projects'))

# 平台管理
@admin.route('/platforms')
@admin_required
def platforms():
    platforms = Platform.query.all()
    return render_template('admin/platforms.html', platforms=platforms)

@admin.route('/platforms/add', methods=['GET', 'POST'])
@admin_required
def add_platform():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        description = request.form.get('description')
        
        # 检查平台名是否已存在
        if Platform.query.filter_by(name=name).first():
            flash('平台名已存在', 'danger')
            return redirect(url_for('admin.add_platform'))
        
        # 创建新平台
        platform = Platform(name=name, url=url, description=description)
        
        db.session.add(platform)
        db.session.commit()
        
        flash('平台添加成功', 'success')
        return redirect(url_for('admin.platforms'))
    
    return render_template('admin/add_platform.html')

@admin.route('/platforms/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_platform(id):
    platform = Platform.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        description = request.form.get('description')
        
        # 检查平台名是否已被其他平台使用
        existing_platform = Platform.query.filter_by(name=name).first()
        if existing_platform and existing_platform.id != platform.id:
            flash('平台名已存在', 'danger')
            return redirect(url_for('admin.edit_platform', id=id))
        
        # 更新平台信息
        platform.name = name
        platform.url = url
        platform.description = description
        
        db.session.commit()
        
        flash('平台更新成功', 'success')
        return redirect(url_for('admin.platforms'))
    
    return render_template('admin/edit_platform.html', platform=platform)

@admin.route('/platforms/delete/<int:id>', methods=['POST'])
@admin_required
def delete_platform(id):
    platform = Platform.query.get_or_404(id)
    
    db.session.delete(platform)
    db.session.commit()
    
    flash('平台删除成功', 'success')
    return redirect(url_for('admin.platforms'))
