from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, stream_with_context
from flask_login import login_required, current_user
from models import User, Platform, db
import requests
import logging
import urllib.parse
import re

user = Blueprint('user', __name__, url_prefix='/user')

# 特殊资源映射
SPECIAL_RESOURCES = {
    '/setting.json': '{"auth_mode":"db_auth","self_registration":false,"harbor_version":"v2.5.0"}',
    '/api/v2.0/systeminfo': '{"with_notary":false,"with_chartmuseum":false,"registry_url":"110.41.187.42:5000","external_url":"https://110.41.187.42:5000","auth_mode":"db_auth","project_creation_restriction":"everyone","self_registration":false,"has_ca_root":false,"harbor_version":"v2.5.0","registry_storage_provider_name":"filesystem","read_only":false,"with_trivy":false,"notification_enable":true}',
    '/i18n/lang/en-us-lang.json': '{"APP_TITLE":"Harbor","SIGN_IN":"Sign In","SIGN_UP":"Sign Up","FORGOT_PASSWORD":"Forgot Password","WELCOME":"Welcome"}',
    '/i18n/lang/zh-cn-lang.json': '{"APP_TITLE":"Harbor","SIGN_IN":"登录","SIGN_UP":"注册","FORGOT_PASSWORD":"忘记密码","WELCOME":"欢迎"}',
    '/dark-theme.css': '/* Empty dark theme CSS */',
    '/light-theme.css': '/* Empty light theme CSS */'
}

# Angular懒加载模块映射
ANGULAR_CHUNKS = {
    '/180.1cf2619f4b2da1d4.js': '// Empty Angular chunk module',
    '/404.7f7096d412d72473.js': '// Empty Angular chunk module'
}

# Harbor登录页面HTML
HARBOR_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harbor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 350px;
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo h1 {
            color: #0077b6;
            margin: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button {
            background-color: #0077b6;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 3px;
            width: 100%;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #005f8d;
        }
        .error {
            color: red;
            margin-top: 15px;
            text-align: center;
        }
        .info {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>Harbor</h1>
            <p>企业级容器镜像仓库</p>
        </div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">登录</button>
            <div class="error" id="errorMessage"></div>
        </form>
        <div class="info">
            <p>Harbor 是 VMware 开源的企业级 Docker Registry 项目</p>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('errorMessage').textContent = '登录功能在代理模式下不可用，请使用直接访问模式';
        });
    </script>
</body>
</html>
"""

@user.route('/')
@login_required
def dashboard():
    # 获取用户可访问的平台
    platforms = current_user.get_accessible_platforms()
    return render_template('user/dashboard.html', platforms=platforms)

@user.route('/redirect/<int:platform_id>')
@login_required
def redirect_to_platform(platform_id):
    """直接重定向到平台（优先使用内网URL）"""
    # 获取平台信息
    platform = Platform.query.get_or_404(platform_id)

    # 检查用户是否有权限访问该平台
    accessible_platforms = current_user.get_accessible_platforms()
    if platform not in accessible_platforms:
        abort(403)  # 权限不足，返回403错误

    # 获取目标URL（优先使用内网URL）
    target_url = platform.get_proxy_url()

    # 记录访问日志
    logging.info(f"用户 {current_user.username} 访问平台 {platform.name} ({target_url})")
    print(f"用户 {current_user.username} 访问平台 {platform.name} ({target_url})")

    # 直接重定向到平台URL
    return redirect(target_url)

@user.route('/proxy/<int:platform_id>')
@login_required
def proxy_platform(platform_id):
    """通过服务器代理访问平台"""
    # 添加调试信息
    print(f"进入proxy_platform函数，platform_id={platform_id}")

    # 获取平台信息
    platform = Platform.query.get_or_404(platform_id)
    print(f"找到平台: {platform.name}, URL={platform.url}")

    # 检查用户是否有权限访问该平台
    accessible_platforms = current_user.get_accessible_platforms()
    if platform not in accessible_platforms:
        print(f"用户 {current_user.username} 没有权限访问平台 {platform.name}")
        abort(403)  # 权限不足，返回403错误

    # 记录访问日志
    logging.info(f"用户 {current_user.username} 正在通过代理访问平台 {platform.name} ({platform.url})")
    print(f"用户 {current_user.username} 正在通过代理访问平台 {platform.name} ({platform.url})")

    # 获取目标URL和路径
    # 使用内网URL进行代理访问，如果内网URL不存在，则使用外网URL
    target_url = platform.get_proxy_url()
    path = request.args.get('path', '')

    # 保存原始查询参数，除了path
    query_params = {}
    for key, value in request.args.items():
        if key != 'path':
            query_params[key] = value

    # 处理路径中可能包含的查询参数
    if '?' in path:
        path_part, query_part = path.split('?', 1)
        # 解析查询部分
        from urllib.parse import parse_qs
        parsed_query = parse_qs(query_part)
        # 合并查询参数
        for key, values in parsed_query.items():
            query_params[key] = values[0]
        path = path_part

    # 确保路径以/开头
    if path and not path.startswith('/'):
        path = '/' + path

    # 构建完整的URL
    if path:
        if target_url.endswith('/') and path.startswith('/'):
            full_url = target_url + path[1:]
        else:
            full_url = target_url + path
    else:
        full_url = target_url

    # 添加查询参数
    if query_params:
        from urllib.parse import urlencode
        query_string = urlencode(query_params)
        if '?' in full_url:
            full_url += '&' + query_string
        else:
            full_url += '?' + query_string

    print(f"代理访问URL: {full_url}")

    # 处理特殊资源请求

    # 检查是否是特殊资源请求
    request_path = request.path
    if request_path.startswith('/user/proxy/'):
        # 从代理路径中提取实际路径
        parts = request_path.split('/user/proxy/')
        if len(parts) > 1 and 'path=' in parts[1]:
            # 提取path参数
            path_param = parts[1].split('path=')[1].split('&')[0]
            if path_param in SPECIAL_RESOURCES:
                print(f"处理特殊资源请求: {path_param}")
                content_type = 'application/json'
                if path_param.endswith('.css'):
                    content_type = 'text/css'
                response = Response(SPECIAL_RESOURCES[path_param], content_type=content_type)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response

            # 检查是否是去掉查询参数后的特殊资源
            base_path = path_param.split('?')[0]
            if base_path in SPECIAL_RESOURCES:
                print(f"处理特殊资源请求(去掉查询参数): {base_path}")
                content_type = 'application/json'
                if base_path.endswith('.css'):
                    content_type = 'text/css'
                response = Response(SPECIAL_RESOURCES[base_path], content_type=content_type)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response

            # 检查是否是Angular懒加载模块
            for chunk_path in ANGULAR_CHUNKS:
                if chunk_path[1:] in path_param:  # 去掉前导斜杠进行比较
                    print(f"处理Angular懒加载模块: {path_param}")
                    response = Response(ANGULAR_CHUNKS[chunk_path], content_type='application/javascript')
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
    elif path in SPECIAL_RESOURCES:
        print(f"处理特殊资源请求: {path}")
        content_type = 'application/json'
        if path.endswith('.css'):
            content_type = 'text/css'
        response = Response(SPECIAL_RESOURCES[path], content_type=content_type)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    # 处理OPTIONS请求（CORS预检请求）
    if request.method == 'OPTIONS':
        print(f"处理OPTIONS预检请求: {full_url}")
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24小时
        return response

    # 特殊处理Harbor应用
    if 'harbor' in platform.name.lower():
        print("检测到Harbor应用，使用Nginx反向代理")
        # 构建Nginx反向代理URL
        nginx_proxy_url = f"http://localhost:8080/harbor{path}"
        if request.query_string:
            nginx_proxy_url += f"?{request.query_string.decode('utf-8')}"

        # 返回iframe页面，嵌入Nginx代理的内容
        return render_template('proxy_frame.html',
                              platform=platform,
                              proxy_url=nginx_proxy_url,
                              original_url=platform.url)

    try:
        # 发起请求
        headers = {
            'User-Agent': request.headers.get('User-Agent', 'Flask-Proxy'),
            'Accept': request.headers.get('Accept', '*/*'),
            'Accept-Encoding': request.headers.get('Accept-Encoding', 'gzip, deflate'),
            'Accept-Language': request.headers.get('Accept-Language', 'zh-CN,zh;q=0.9'),
            'Origin': request.headers.get('Origin', f"http://{request.host}"),
            'Referer': request.headers.get('Referer', full_url),
        }

        # 添加可能的认证头
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header

        # 添加其他可能的头
        for key, value in request.headers.items():
            if key.lower() not in ['user-agent', 'accept', 'accept-encoding', 'accept-language', 'origin', 'referer', 'authorization', 'host', 'connection', 'content-length']:
                headers[key] = value

        # 发起请求
        resp = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            params=request.args,
            data=request.form,
            cookies=request.cookies,
            allow_redirects=True,  # 允许重定向
            timeout=30
        )

        # 检查响应状态码
        if resp.status_code >= 400:
            error_msg = f"代理请求失败: 状态码 {resp.status_code}"
            logging.error(error_msg)
            print(error_msg)
            return render_template('error.html', error=error_msg)

        # 获取响应内容
        content = resp.content
        content_type = resp.headers.get('Content-Type', 'text/html')

        # 检查是否是静态资源（CSS、JS、图片等）或API请求
        is_static = any(ext in full_url.lower() for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'])
        is_api = '/api/' in full_url.lower() or '/i18n/' in full_url.lower() or '.json' in full_url.lower()
        is_angular_chunk = bool(re.match(r'.*?/\d+\.[a-f0-9]+\.js', full_url.lower()))

        # 检查是否是已知的Angular懒加载模块
        for chunk_path in ANGULAR_CHUNKS:
            if chunk_path[1:] in full_url:  # 去掉前导斜杠进行比较
                print(f"检测到已知的Angular懒加载模块: {full_url}")
                response = Response(ANGULAR_CHUNKS[chunk_path], content_type='application/javascript')
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.status_code = 200
                return response

        # 检查是否是未知的Angular懒加载模块
        if is_angular_chunk and resp.status_code == 404:
            print(f"检测到未知的Angular懒加载模块404: {full_url}")
            # 返回一个空的JS模块，避免Angular报错
            response = Response('// Empty module for Angular lazy loading', content_type='application/javascript')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.status_code = 200
            return response

        if is_static or is_api or is_angular_chunk or not 'text/html' in content_type:
            print(f"处理静态资源或API请求: {full_url}")
            # 对于静态资源和API请求，直接返回内容，不做修改
            response = Response(content)

            # 设置CORS头，允许跨域请求
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

            # 复制其他响应头
            for key, value in resp.headers.items():
                if key.lower() not in ('content-encoding', 'content-length', 'transfer-encoding', 'connection', 'access-control-allow-origin', 'access-control-allow-methods', 'access-control-allow-headers'):
                    response.headers[key] = value

            response.status_code = resp.status_code
            return response

        # 如果是HTML内容，修改链接使其通过代理
        if 'text/html' in content_type:
            try:
                # 尝试解码内容，处理可能的编码问题
                try:
                    charset = resp.encoding or 'utf-8'
                    html_content = content.decode(charset)
                except UnicodeDecodeError:
                    # 如果指定编码失败，尝试使用更通用的编码
                    try:
                        html_content = content.decode('utf-8', errors='replace')
                    except:
                        html_content = content.decode('latin-1', errors='replace')

                # 修改所有相对链接为绝对链接
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # 提取基础URL，用于解析相对URL
                from urllib.parse import urljoin, urlparse, urlunparse
                base_url = resp.url
                parsed_base = urlparse(base_url)
                base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

                # 检查是否是Angular应用
                is_angular = False
                angular_markers = ['ng-version', 'angular', '_nghost', '_ngcontent']
                for marker in angular_markers:
                    if marker in html_content:
                        is_angular = True
                        print(f"检测到Angular应用: {marker} 在响应内容中")
                        break

                # 检查是否是Angular应用，如果是，添加特殊处理
                if is_angular:
                    # 添加特殊的脚本来处理Angular的懒加载模块
                    script_tag = soup.new_tag('script')
                    script_tag.string = """
                    (function() {
                        // 拦截Angular的懒加载请求
                        var originalFetch = window.fetch;
                        window.fetch = function(url, options) {
                            // 检查是否是懒加载模块请求
                            if (url && typeof url === 'string' && url.match(/\\d+\\.[a-f0-9]+\\.js$/)) {
                                console.log('拦截Angular懒加载请求:', url);
                                // 修改URL，添加代理前缀
                                var pathParts = url.split('/');
                                var fileName = pathParts[pathParts.length - 1];
                                var proxyUrl = '/user/proxy/""" + str(platform_id) + """?path=/' + fileName;
                                console.log('重定向到:', proxyUrl);
                                return originalFetch(proxyUrl, options);
                            }
                            return originalFetch.apply(this, arguments);
                        };

                        // 拦截动态脚本加载
                        var originalCreateElement = document.createElement;
                        document.createElement = function(tagName) {
                            var element = originalCreateElement.apply(document, arguments);
                            if (tagName.toLowerCase() === 'script') {
                                var originalSetter = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'src').set;
                                Object.defineProperty(element, 'src', {
                                    set: function(url) {
                                        if (url && typeof url === 'string' && url.match(/\\d+\\.[a-f0-9]+\\.js$/)) {
                                            console.log('拦截脚本加载:', url);
                                            var pathParts = url.split('/');
                                            var fileName = pathParts[pathParts.length - 1];
                                            var proxyUrl = '/user/proxy/""" + str(platform_id) + """?path=/' + fileName;
                                            console.log('重定向到:', proxyUrl);
                                            originalSetter.call(this, proxyUrl);
                                        } else {
                                            originalSetter.call(this, url);
                                        }
                                    }
                                });
                            }
                            return element;
                        };
                    })();
                    """
                    soup.head.append(script_tag)

                # 修改所有链接
                for tag in soup.find_all(['a', 'link', 'script', 'img', 'form', 'base']):
                    # 处理base标签
                    if tag.name == 'base' and tag.has_attr('href'):
                        base_url = tag['href']
                        continue

                    # 处理href属性
                    if tag.has_attr('href') and not tag['href'].startswith(('javascript:', '#', 'mailto:', 'tel:', 'data:')):
                        # 跳过已经是代理URL的链接
                        if 'user/proxy' in tag['href']:
                            continue

                        # 处理相对URL和绝对URL
                        if tag['href'].startswith(('http://', 'https://')):
                            # 外部链接保持不变
                            if not tag['href'].startswith(base_domain):
                                continue
                            # 同域名的绝对URL
                            full_href = tag['href']
                            path_part = urlparse(full_href).path
                            tag['href'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)
                        elif tag['href'].startswith('/'):
                            # 绝对路径
                            tag['href'] = url_for('user.proxy_platform', platform_id=platform_id, path=tag['href'])
                        else:
                            # 相对路径
                            full_url = urljoin(base_url, tag['href'])
                            path_part = urlparse(full_url).path
                            tag['href'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)

                    # 处理src属性
                    if tag.has_attr('src') and not tag['src'].startswith(('data:', '//')):
                        # 跳过已经是代理URL的链接
                        if 'user/proxy' in tag['src']:
                            continue

                        # 检查是否是Angular懒加载模块
                        if re.match(r'.*?/\d+\.[a-f0-9]+\.js', tag['src']):
                            # 提取文件名
                            path_parts = tag['src'].split('/')
                            file_name = path_parts[-1]
                            tag['src'] = url_for('user.proxy_platform', platform_id=platform_id, path='/' + file_name)
                            continue

                        # 处理相对URL和绝对URL
                        if tag['src'].startswith(('http://', 'https://')):
                            # 外部链接保持不变
                            if not tag['src'].startswith(base_domain):
                                continue
                            # 同域名的绝对URL
                            full_src = tag['src']
                            path_part = urlparse(full_src).path
                            tag['src'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)
                        elif tag['src'].startswith('/'):
                            # 绝对路径
                            tag['src'] = url_for('user.proxy_platform', platform_id=platform_id, path=tag['src'])
                        else:
                            # 相对路径
                            full_url = urljoin(base_url, tag['src'])
                            path_part = urlparse(full_url).path
                            tag['src'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)

                    # 处理action属性（表单）
                    if tag.has_attr('action') and not tag['action'].startswith(('javascript:', '#')):
                        # 跳过已经是代理URL的链接
                        if 'user/proxy' in tag['action']:
                            continue

                        # 处理相对URL和绝对URL
                        if tag['action'].startswith(('http://', 'https://')):
                            # 外部链接保持不变
                            if not tag['action'].startswith(base_domain):
                                continue
                            # 同域名的绝对URL
                            full_action = tag['action']
                            path_part = urlparse(full_action).path
                            tag['action'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)
                        elif tag['action'].startswith('/'):
                            # 绝对路径
                            tag['action'] = url_for('user.proxy_platform', platform_id=platform_id, path=tag['action'])
                        else:
                            # 相对路径
                            full_url = urljoin(base_url, tag['action'])
                            path_part = urlparse(full_url).path
                            tag['action'] = url_for('user.proxy_platform', platform_id=platform_id, path=path_part)

                # 添加代理工具栏
                toolbar = soup.new_tag('div')
                toolbar['style'] = 'position:fixed; top:0; left:0; right:0; background-color:#343a40; color:white; padding:10px; border-bottom:2px solid #007bff; z-index:999999; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 5px rgba(0,0,0,0.2);'

                # 添加标题
                title = soup.new_tag('div')
                title['style'] = 'font-weight:bold; font-size:14px;'
                title.string = f"代理访问: {platform.name} ({platform.url})"
                toolbar.append(title)

                # 添加按钮组
                buttons = soup.new_tag('div')

                # 返回按钮
                back_btn = soup.new_tag('a')
                back_btn['href'] = url_for('user.dashboard')
                back_btn['style'] = 'text-decoration:none; color:white; background-color:#6c757d; padding:6px 12px; border-radius:4px; margin-right:8px; font-size:13px; display:inline-block;'
                back_btn.string = '返回平台列表'
                buttons.append(back_btn)

                # 刷新按钮
                refresh_btn = soup.new_tag('a')
                refresh_btn['href'] = url_for('user.proxy_platform', platform_id=platform_id, path=path)
                refresh_btn['style'] = 'text-decoration:none; color:white; background-color:#17a2b8; padding:6px 12px; border-radius:4px; margin-right:8px; font-size:13px; display:inline-block;'
                refresh_btn.string = '刷新页面'
                buttons.append(refresh_btn)

                # 直接访问按钮
                direct_btn = soup.new_tag('a')
                direct_btn['href'] = platform.url
                direct_btn['target'] = '_blank'
                direct_btn['style'] = 'text-decoration:none; color:white; background-color:#28a745; padding:6px 12px; border-radius:4px; font-size:13px; display:inline-block;'
                direct_btn.string = '直接访问'
                buttons.append(direct_btn)

                toolbar.append(buttons)

                # 添加状态信息
                status = soup.new_tag('div')
                status['id'] = 'proxy-status'
                status['style'] = 'position:fixed; bottom:10px; right:10px; background-color:rgba(0,0,0,0.7); color:white; padding:5px 10px; border-radius:4px; font-size:12px; z-index:999999; display:none;'
                status.string = '代理模式'
                soup.body.append(status)

                # 添加JavaScript以显示状态信息
                script = soup.new_tag('script')
                script.string = """
                    setTimeout(function() {
                        var status = document.getElementById('proxy-status');
                        if (status) {
                            status.style.display = 'block';
                            setTimeout(function() {
                                status.style.display = 'none';
                            }, 3000);
                        }
                    }, 1000);
                """
                soup.body.append(script)

                # 添加工具栏到body
                if soup.body:
                    # 检查是否是Angular应用，如果是，添加特殊处理
                    if is_angular:
                        print("为Angular应用添加工具栏")
                        # 在Angular应用中，我们需要在app-root之前添加工具栏
                        app_root = soup.select_one('app-root')
                        if app_root:
                            app_root.insert_before(toolbar)
                        else:
                            # 如果找不到app-root，则添加到body开头
                            soup.body.insert(0, toolbar)
                    else:
                        # 对于非Angular应用，直接添加到body开头
                        soup.body.insert(0, toolbar)

                    # 添加内边距，避免内容被工具栏遮挡
                    if soup.body.has_attr('style'):
                        soup.body['style'] += '; padding-top: 50px;'
                    else:
                        soup.body['style'] = 'padding-top: 50px;'

                    # 如果是Angular应用，添加额外的CSS来修复可能的样式问题
                    if is_angular:
                        style_tag = soup.new_tag('style')
                        style_tag.string = """
                            body { padding-top: 50px !important; }
                            .harbor-container { padding-top: 50px !important; }
                            .container-fluid { padding-top: 0 !important; }
                            app-root { display: block; padding-top: 0 !important; }
                        """
                        soup.head.append(style_tag)

                # 转换回HTML，处理可能的编码问题
                try:
                    content = str(soup).encode(charset)
                except UnicodeEncodeError:
                    # 如果编码失败，使用utf-8
                    content = str(soup).encode('utf-8')
            except Exception as e:
                logging.error(f"修改HTML内容时出错: {str(e)}")
                print(f"修改HTML内容时出错: {str(e)}")
                # 如果修改失败，使用原始内容

        # 创建响应对象
        response = Response(content)

        # 复制响应头
        for key, value in resp.headers.items():
            if key.lower() not in ('content-encoding', 'content-length', 'transfer-encoding', 'connection'):
                response.headers[key] = value

        # 设置状态码
        response.status_code = resp.status_code
        return response

    except requests.RequestException as e:
        # 处理请求异常
        error_msg = f"代理请求失败: {str(e)}"
        logging.error(error_msg)
        print(error_msg)
        return render_template('error.html', error=error_msg)
    except Exception as e:
        # 捕获并记录任何异常
        error_msg = f"代理访问时出错: {str(e)}"
        logging.error(error_msg)
        print(error_msg)
        return render_template('error.html', error=error_msg)

@user.route('/direct/<int:platform_id>')
@login_required
def direct_to_platform(platform_id):
    """直接重定向到平台（优先使用内网URL）"""
    # 获取平台信息
    platform = Platform.query.get_or_404(platform_id)

    # 检查用户是否有权限访问该平台
    accessible_platforms = current_user.get_accessible_platforms()
    if platform not in accessible_platforms:
        abort(403)  # 权限不足，返回403错误

    # 获取目标URL（优先使用内网URL）
    target_url = platform.get_proxy_url()

    # 记录访问日志
    logging.info(f"用户 {current_user.username} 直接访问平台 {platform.name} ({target_url})")
    print(f"用户 {current_user.username} 直接访问平台 {platform.name} ({target_url})")

    # 直接重定向到平台URL
    return redirect(target_url)

@user.route('/api/proxy/<int:platform_id>')
@login_required
def api_proxy(platform_id):
    """API代理路由，用于处理AJAX请求"""
    # 添加调试信息
    print(f"进入api_proxy函数，platform_id={platform_id}")

    # 获取平台信息
    platform = Platform.query.get_or_404(platform_id)
    print(f"找到平台: {platform.name}, URL={platform.url}")

    # 检查用户是否有权限访问该平台
    accessible_platforms = current_user.get_accessible_platforms()
    if platform not in accessible_platforms:
        print(f"用户 {current_user.username} 没有权限访问平台 {platform.name}")
        abort(403)  # 权限不足，返回403错误

    # 获取目标URL
    target_url = request.args.get('url')
    if not target_url:
        target_url = platform.url

    # 记录访问日志
    logging.info(f"用户 {current_user.username} 通过API代理访问: {target_url}")
    print(f"用户 {current_user.username} 通过API代理访问: {target_url}, 请求方法: {request.method}")

    # 构建请求
    method = request.method
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'Flask-Proxy'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Accept-Encoding': request.headers.get('Accept-Encoding', 'gzip, deflate'),
        'Accept-Language': request.headers.get('Accept-Language', 'zh-CN,zh;q=0.9'),
    }

    # 添加可能的认证头
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header

    # 处理请求
    try:
        # 发起请求
        resp = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.form,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )

        # 创建响应对象
        response = Response(stream_with_context(resp.iter_content(chunk_size=1024)))

        # 复制响应头
        for key, value in resp.headers.items():
            if key.lower() not in ('content-encoding', 'content-length', 'transfer-encoding', 'connection'):
                response.headers[key] = value

        # 设置状态码
        response.status_code = resp.status_code
        return response

    except Exception as e:
        logging.error(f"API代理访问出错: {str(e)}")
        return Response(f"代理访问出错: {str(e)}", status=500)
