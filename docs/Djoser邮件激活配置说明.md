# Djoser 邮件激活用户账号配置说明

## ✅ 已完成的配置

### 1. 后端配置

#### 安装依赖

已在 `requirements.txt` 中添加：
```
djangorestframework==3.16.1
djoser==2.2.3
django-templated-mail==1.1.1
```

#### Django Settings 配置

**INSTALLED_APPS** - 已添加必要的应用：
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',  # Token 认证
    'djoser',  # Djoser 用户认证
    # ...
]
```

**REST_FRAMEWORK** - 配置 Token 认证：
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # ...
}
```

**邮件配置**：
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = '842015629@qq.com'
EMAIL_HOST_PASSWORD = 'siwlfnlqfxrobahj'  # QQ邮箱授权码
DEFAULT_FROM_EMAIL = '842015629@qq.com'
```

**Djoser 配置**：
```python
DJOSER = {
    'SEND_ACTIVATION_EMAIL': True,  # 发送激活邮件
    'ACTIVATION_URL': 'activate/{uid}/{token}',  # 激活链接路径
    'DOMAIN': 'localhost:5176',  # 前端域名
    'SITE_NAME': 'CYPHER GAME BUY',
    'LOGIN_FIELD': 'email',  # 使用邮箱登录
    'USER_CREATE_PASSWORD_RETYPE': True,  # 注册时需要两次输入密码
    # ... 其他配置
}
```

#### URL 配置

已在 `game_recharge/urls.py` 中添加 Djoser 路由：
```python
urlpatterns = [
    # ...
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    # ...
]
```

#### 邮件模板

已创建赛博朋克风格的激活邮件模板：
- 文件位置：`templates/djoser_email_activation.html`
- 样式：深色渐变背景、霓虹灯发光效果、青色/粉色/紫色配色

### 2. 前端配置

#### 创建的页面

1. **注册页面** - `frontend/src/views/RegisterPage.vue`
   - 用户注册表单
   - 密码验证（两次输入、最少8位）
   - 注册成功后显示待激活提示
   - 引导用户打开邮箱

2. **激活页面** - `frontend/src/views/ActivateAccountPage.vue`
   - 自动激活账号
   - 激活成功显示
   - 5秒倒计时跳转登录页
   - 激活失败错误处理

3. **登录页面** - `frontend/src/views/LoginPage.vue`
   - 邮箱密码登录
   - Token 认证
   - 登录成功跳转首页

#### 路由配置

已在 `frontend/src/router/index.ts` 中添加路由：
```typescript
{
  path: 'register',
  name: 'register',
  component: RegisterPage,
},
{
  path: 'login',
  name: 'login',
  component: LoginPage,
},
{
  path: 'activate/:uid/:token',
  name: 'activate-account',
  component: ActivateAccountPage,
},
```

## 🚀 安装和启动

### 步骤 1：安装 Python 依赖

```bash
cd e:\小程序开发\游戏充值网站
pip install -r requirements.txt
```

### 步骤 2：运行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 步骤 3：启动 Django 后端

```bash
python manage.py runserver 8000
```

### 步骤 4：启动 Vue 前端

```bash
cd frontend
npm run dev
```

## 🎯 使用流程

### 用户注册流程

1. **访问注册页面**
   ```
   http://localhost:5176/register
   ```

2. **填写注册信息**
   - 用户名
   - 邮箱地址
   - 密码（至少8位）
   - 确认密码

3. **点击注册按钮**
   - 后端创建未激活的用户账号
   - 自动发送激活邮件到用户邮箱

4. **显示待激活页面**
   - 提示用户打开邮箱
   - 显示操作步骤指南
   - 提供"打开邮箱"快捷按钮

### 邮件激活流程

5. **用户打开邮箱**
   - 查找来自 "CYPHER GAME BUY" 的邮件
   - 邮件标题：激活您的账号

6. **点击激活按钮**
   - 邮件中包含激活链接
   - 链接格式：`http://localhost:5176/activate/{uid}/{token}`
   - 链接有效期：24小时

7. **自动跳转激活页面**
   - 前端接收 uid 和 token 参数
   - 自动调用后端激活 API
   - 显示激活进度

8. **激活成功**
   - 显示成功提示
   - 5秒倒计时
   - 自动跳转到登录页面

9. **登录使用**
   - 使用邮箱和密码登录
   - 获取 Token
   - 开始使用平台

## 📝 API 端点说明

### Djoser 提供的 API

#### 用户注册
```http
POST /api/auth/users/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "re_password": "password123"
}
```

**响应**：
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "id": 1
}
```

#### 账号激活
```http
POST /api/auth/users/activation/
Content-Type: application/json

{
  "uid": "MQ",
  "token": "c4u-39b9d1fc0e4e9f0ba870"
}
```

**响应**：
```json
{
  "detail": "Your account has been activated."
}
```

#### 用户登录（获取 Token）
```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

**响应**：
```json
{
  "auth_token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### 用户登出
```http
POST /api/auth/token/logout/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

#### 获取当前用户信息
```http
GET /api/auth/users/me/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**响应**：
```json
{
  "email": "test@example.com",
  "id": 1,
  "username": "testuser"
}
```

## 🧪 测试流程

### 1. 测试注册功能

```bash
# 访问注册页面
http://localhost:5176/register

# 填写测试信息
用户名：testuser
邮箱：your_email@qq.com
密码：testpass123
确认密码：testpass123

# 点击注册
```

### 2. 检查邮件

```bash
# 登录邮箱查看激活邮件
# QQ邮箱：https://mail.qq.com
# 查找主题：激活您的账号
```

### 3. 点击激活链接

```bash
# 邮件中的链接会自动跳转到
http://localhost:5176/activate/{uid}/{token}

# 自动激活并跳转登录页
```

### 4. 登录测试

```bash
# 访问登录页面
http://localhost:5176/login

# 使用注册的邮箱和密码登录
```

## 🔍 故障排查

### 问题 1：收不到激活邮件

**可能原因**：
- QQ邮箱授权码错误
- SMTP 配置错误
- 邮箱被拦截

**解决方案**：
1. 检查 settings.py 中的邮箱配置
2. 确认授权码正确：`siwlfnlqfxrobahj`
3. 检查垃圾邮件文件夹
4. 查看 Django 日志输出

### 问题 2：激活链接无效

**可能原因**：
- 链接已过期（24小时）
- 链接已被使用
- uid 或 token 参数错误

**解决方案**：
1. 重新注册账号
2. 检查链接是否完整
3. 确认链接未过期

### 问题 3：激活 API 调用失败

**可能原因**：
- 后端服务未启动
- CORS 配置问题
- API 路由配置错误

**解决方案**：
1. 确认后端运行在 http://localhost:8000
2. 检查 CORS 配置
3. 查看浏览器控制台错误信息

### 问题 4：登录失败

**可能原因**：
- 账号未激活
- 邮箱或密码错误
- Token 认证未配置

**解决方案**：
1. 确认账号已激活
2. 检查邮箱和密码是否正确
3. 确认 Token 认证已配置

## 📊 数据库操作

### 查看用户激活状态

```bash
python manage.py shell

>>> from django.contrib.auth.models import User
>>> user = User.objects.get(email='test@example.com')
>>> print(user.is_active)  # 激活后应该是 True
```

### 手动激活用户

```bash
python manage.py shell

>>> from django.contrib.auth.models import User
>>> user = User.objects.get(email='test@example.com')
>>> user.is_active = True
>>> user.save()
```

## 🎨 自定义邮件模板

邮件模板位置：`templates/djoser_email_activation.html`

### 可自定义内容：

1. **样式**：修改 CSS 样式
2. **文案**：修改邮件内容
3. **图片**：添加 Logo 或其他图片
4. **链接**：修改激活链接文本

### 模板变量：

- `{{ user.username }}` - 用户名
- `{{ user.email }}` - 用户邮箱
- `{{ domain }}` - 网站域名
- `{{ url }}` - 激活链接路径

## 🔒 安全建议

### 生产环境配置

1. **使用环境变量**
```python
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

2. **使用 HTTPS**
```python
DJOSER = {
    'DOMAIN': 'yourdomain.com',
    # ...
}
```

3. **限制激活链接有效期**
```python
# 可以通过自定义 Djoser 配置来修改
# 默认是 24 小时
```

4. **添加验证码**
- 注册时添加图形验证码
- 防止恶意批量注册

5. **邮件发送限流**
- 限制每个IP的注册次数
- 防止邮件轰炸

## ✨ 功能特点

### 用户体验

✅ **赛博朋克风格界面**
- 深色渐变背景
- 霓虹灯发光效果
- 青色/粉色/紫色配色

✅ **流畅的注册流程**
- 实时表单验证
- 友好的错误提示
- 清晰的操作指引

✅ **精美的激活邮件**
- 响应式邮件设计
- 醒目的激活按钮
- 详细的操作说明

✅ **自动化激活流程**
- 点击链接自动激活
- 激活成功自动跳转
- 5秒倒计时提示

### 技术特点

✅ **前后端分离**
- Vue 3 前端
- Django REST API 后端
- Token 认证机制

✅ **安全可靠**
- 邮件验证机制
- 密码加密存储
- CSRF 保护

✅ **易于扩展**
- Djoser 提供完整的用户管理 API
- 支持密码重置
- 支持用户信息更新

## 📚 相关文档

- [Djoser 官方文档](https://djoser.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue Router](https://router.vuejs.org/)
- [QQ邮箱 SMTP 设置](https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256)

## 🎊 完成清单

- [x] ✅ 安装 Djoser 和相关依赖
- [x] ✅ 配置邮件服务（QQ邮箱）
- [x] ✅ 配置 Djoser 设置
- [x] ✅ 添加 API 路由
- [x] ✅ 创建邮件模板
- [x] ✅ 创建注册页面
- [x] ✅ 创建激活页面
- [x] ✅ 创建登录页面
- [x] ✅ 配置前端路由
- [x] ✅ 实现自动跳转逻辑

现在您可以开始测试完整的用户注册和邮件激活功能了！

**开始使用**：
1. 启动后端：`python manage.py runserver 8000`
2. 启动前端：`cd frontend && npm run dev`
3. 访问注册页面：http://localhost:5176/register

祝您使用愉快！🚀
