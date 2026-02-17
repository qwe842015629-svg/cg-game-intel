# Django CORS 跨域配置说明

## ✅ 已完成的配置

### 1. 安装依赖
已在 `requirements.txt` 中包含：
```
django-cors-headers==4.9.0
```

### 2. Django Settings 配置

#### INSTALLED_APPS
已添加 `corsheaders` 到应用列表：
```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]
```

#### MIDDLEWARE
已正确添加 CORS 中间件（**必须在 CommonMiddleware 之前**）：
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ✅ 正确位置
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

#### CORS 配置项
```python
# CORS settings - 配置跨域请求
# 开发环境允许前端访问
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5176',
    'http://127.0.0.1:5176',
]

# 允许携带Cookie和认证信息
CORS_ALLOW_CREDENTIALS = True

# 允许的HTTP方法
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# 允许浏览器缓存预检请求的时间（秒）
CORS_PREFLIGHT_MAX_AGE = 86400
```

## 🚀 启动服务

### 1. 启动 Django 后端
```bash
cd e:\小程序开发\游戏充值网站
python manage.py runserver 8000
```

后端将运行在：**http://localhost:8000/**

### 2. 启动 Vue 前端
```bash
cd e:\小程序开发\游戏充值网站\frontend
npm run dev
```

前端将运行在：**http://localhost:5176/**

## 🧪 测试跨域请求

### 在 Vue 前端测试 API 调用

#### 方式1：使用 axios
```typescript
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  withCredentials: true, // 允许携带 Cookie
})

// 测试 GET 请求
api.get('/api/games/')
  .then(response => {
    console.log('✅ 跨域请求成功:', response.data)
  })
  .catch(error => {
    console.error('❌ 请求失败:', error)
  })

// 测试 POST 请求
api.post('/api/orders/', {
  game_id: 1,
  amount: 100
})
  .then(response => {
    console.log('✅ POST 请求成功:', response.data)
  })
  .catch(error => {
    console.error('❌ POST 请求失败:', error)
  })
```

#### 方式2：使用 fetch
```typescript
fetch('http://localhost:8000/api/games/', {
  method: 'GET',
  credentials: 'include', // 允许携带 Cookie
  headers: {
    'Content-Type': 'application/json',
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('✅ 跨域请求成功:', data)
  })
  .catch(error => {
    console.error('❌ 请求失败:', error)
  })
```

## 🔍 验证 CORS 配置

### 检查浏览器控制台

#### ✅ 成功的响应头应包含：
```
Access-Control-Allow-Origin: http://localhost:5176
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, ...
```

#### ❌ 常见错误信息：
1. **"No 'Access-Control-Allow-Origin' header"**
   - 原因：CORS 中间件未正确配置
   - 解决：检查 MIDDLEWARE 中是否包含 `corsheaders.middleware.CorsMiddleware`

2. **"Origin is not allowed"**
   - 原因：前端地址不在 CORS_ALLOWED_ORIGINS 列表中
   - 解决：确认前端地址是 http://localhost:5176

3. **"Credentials flag is true, but 'Access-Control-Allow-Credentials' header is ''"**
   - 原因：CORS_ALLOW_CREDENTIALS 未设置为 True
   - 解决：已在配置中设置为 True

## 📝 注意事项

### 开发环境 vs 生产环境

#### 当前配置（开发环境）：
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5176',
    'http://127.0.0.1:5176',
]
```

#### 生产环境配置示例：
```python
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]

# 或使用正则表达式匹配多个子域名
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.yourdomain\.com$",
]
```

### 安全建议

1. **不要使用 CORS_ALLOW_ALL_ORIGINS = True**
   - ✅ 当前配置：指定了具体的前端地址
   - ❌ 错误配置：`CORS_ALLOW_ALL_ORIGINS = True`（允许任何域名访问）

2. **生产环境使用 HTTPS**
   - 开发环境可以使用 http://localhost
   - 生产环境必须使用 https://

3. **限制允许的 HTTP 方法**
   - 只开放应用实际需要的方法
   - 当前配置已限制为：GET, POST, PUT, PATCH, DELETE, OPTIONS

## 🐛 常见问题排查

### 问题1：前端请求返回 404
**原因**：Django API 端点不存在
**解决**：
1. 检查 Django URLs 配置
2. 访问 http://localhost:8000/admin/ 确认后端运行正常
3. 确认 API 路由是否正确注册

### 问题2：CSRF token 错误
**原因**：POST 请求需要 CSRF token
**解决方案1** - 对 API 禁用 CSRF（推荐用于前后端分离）：
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class YourAPIView(View):
    pass
```

**解决方案2** - 在请求中包含 CSRF token：
```typescript
// 从 Cookie 中获取 CSRF token
function getCookie(name: string) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift()
}

// 在 axios 中配置
axios.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken')
```

### 问题3：OPTIONS 预检请求失败
**原因**：浏览器在发送实际请求前会先发送 OPTIONS 请求检查 CORS
**解决**：
- ✅ 已在 CORS_ALLOW_METHODS 中包含 'OPTIONS'
- ✅ 已配置 CORS_PREFLIGHT_MAX_AGE 缓存预检结果

## 📚 相关文档

- [django-cors-headers 官方文档](https://github.com/adamchainz/django-cors-headers)
- [MDN CORS 文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [Django REST framework 文档](https://www.django-rest-framework.org/)

## ✨ 配置完成检查清单

- [x] ✅ 安装 django-cors-headers
- [x] ✅ 添加 'corsheaders' 到 INSTALLED_APPS
- [x] ✅ 添加 CorsMiddleware 到 MIDDLEWARE（正确位置）
- [x] ✅ 配置 CORS_ALLOWED_ORIGINS
- [x] ✅ 配置 CORS_ALLOW_CREDENTIALS
- [x] ✅ 配置 CORS_ALLOW_METHODS
- [x] ✅ 配置 CORS_ALLOW_HEADERS
- [x] ✅ 配置 CORS_PREFLIGHT_MAX_AGE

现在您的 Django 后端已经完全配置好 CORS，可以正常接收来自 http://localhost:5176 的前端请求了！
