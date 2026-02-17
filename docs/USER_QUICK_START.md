# 用户模块快速使用指南

## 🚀 快速开始

### 1. 访问Django后台管理

```bash
# 访问URL
http://127.0.0.1:8000/admin/

# 登录后，在左侧菜单找到"用户管理"
用户管理 > 用户列表
```

### 2. 测试API接口

#### 方式一：使用浏览器
直接访问以下URL查看数据：
```
http://127.0.0.1:8000/api/users/
http://127.0.0.1:8000/api/users/stats/
http://127.0.0.1:8000/api/profiles/
```

#### 方式二：使用测试脚本
```bash
python test_user_api.py
```

#### 方式三：使用curl命令
```bash
# 获取用户列表
curl http://127.0.0.1:8000/api/users/

# 获取用户详情
curl http://127.0.0.1:8000/api/users/1/

# 获取用户统计
curl http://127.0.0.1:8000/api/users/stats/
```

---

## 📋 API端点速查表

| 端点 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/users/` | GET | 获取用户列表 | ❌ |
| `/api/users/{id}/` | GET | 获取用户详情 | ❌ |
| `/api/users/me/` | GET | 获取当前用户信息 | ✅ |
| `/api/users/stats/` | GET | 获取用户统计 | ❌ |
| `/api/profiles/` | GET | 获取用户资料列表 | ❌ |
| `/api/profiles/{id}/` | GET | 获取用户资料详情 | ❌ |
| `/api/profiles/{id}/` | PUT/PATCH | 更新用户资料 | ✅ |

---

## 🔧 前端集成步骤

### 步骤1：创建API服务文件

在Vue项目中创建 `src/api/users.js`：

```javascript
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

export const userApi = {
  // 获取用户列表
  getList: (page = 1) => {
    return axios.get(`${API_BASE}/users/?page=${page}`)
  },
  
  // 获取用户详情
  getDetail: (id) => {
    return axios.get(`${API_BASE}/users/${id}/`)
  },
  
  // 获取当前用户
  getCurrentUser: (token) => {
    return axios.get(`${API_BASE}/users/me/`, {
      headers: { Authorization: `Token ${token}` }
    })
  },
  
  // 获取统计数据
  getStats: () => {
    return axios.get(`${API_BASE}/users/stats/`)
  }
}
```

### 步骤2：在组件中使用

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/users'

const users = ref([])
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    // 获取用户列表
    const { data } = await userApi.getList()
    users.value = data.results || data
    
    // 获取统计信息
    const statsData = await userApi.getStats()
    stats.value = statsData.data
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h2>用户统计</h2>
    <div v-if="stats">
      <p>总用户数: {{ stats.total_users }}</p>
      <p>活跃用户: {{ stats.active_users }}</p>
    </div>
    
    <h2>用户列表</h2>
    <div v-for="user in users" :key="user.id">
      <p>{{ user.username }} - ¥{{ user.balance }}</p>
    </div>
  </div>
</template>
```

---

## 📊 数据库查询示例

### 在Django Shell中操作

```bash
# 启动Django Shell
python manage.py shell
```

```python
# 导入模型
from django.contrib.auth.models import User
from users.models import UserProfile

# 获取所有用户
users = User.objects.all()
for user in users:
    print(f"{user.username} - {user.email}")

# 获取用户资料
profile = UserProfile.objects.get(user__username='admin')
print(f"余额: {profile.balance}")
print(f"积分: {profile.points}")

# 更新用户余额
profile.balance = 1000.00
profile.save()

# 创建新用户（自动创建资料）
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='password123'
)
# UserProfile会自动创建

# 通过用户访问资料
print(f"用户余额: {user.profile.balance}")
```

---

## 🎯 常见使用场景

### 场景1：显示用户列表
```javascript
// 获取所有激活用户
const response = await axios.get('http://127.0.0.1:8000/api/users/')
const users = response.data.results
```

### 场景2：显示用户个人中心
```javascript
// 获取当前登录用户信息
const token = localStorage.getItem('authToken')
const response = await axios.get('http://127.0.0.1:8000/api/users/me/', {
  headers: { Authorization: `Token ${token}` }
})
const currentUser = response.data
```

### 场景3：显示用户统计卡片
```javascript
// 获取用户统计
const response = await axios.get('http://127.0.0.1:8000/api/users/stats/')
const stats = response.data
// 显示: 总用户数、活跃用户数、今日新增等
```

### 场景4：更新用户资料
```javascript
// 更新用户手机号
const token = localStorage.getItem('authToken')
const profileId = 1
await axios.patch(`http://127.0.0.1:8000/api/profiles/${profileId}/`, {
  phone: '13900139000'
}, {
  headers: { Authorization: `Token ${token}` }
})
```

---

## 🐛 故障排查

### 问题1：API返回404
**原因**: URL路径错误
**解决**: 检查URL是否正确，确保包含 `/api/` 前缀

### 问题2：CORS错误
**原因**: 跨域请求被阻止
**解决**: 已在settings.py中配置CORS，确保前端端口在允许列表中

### 问题3：401 Unauthorized
**原因**: 需要登录认证的接口未提供Token
**解决**: 在请求头添加 `Authorization: Token {your_token}`

### 问题4：用户资料不存在
**原因**: 旧用户没有自动创建资料
**解决**: 运行以下命令为所有用户创建资料
```python
from django.contrib.auth.models import User
from users.models import UserProfile

for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user)
```

---

## 📝 开发清单

### 已完成 ✅
- [x] 创建UserProfile模型
- [x] 配置Django Admin
- [x] 创建API视图和序列化器
- [x] 配置URL路由
- [x] 执行数据库迁移
- [x] 添加SimpleUI菜单
- [x] 创建测试脚本
- [x] 编写文档

### 建议扩展 💡
- [ ] 添加用户头像上传功能
- [ ] 实现用户等级系统
- [ ] 开发用户积分规则
- [ ] 添加用户充值记录
- [ ] 实现用户消费统计
- [ ] 开发用户行为分析

---

## 📞 需要帮助？

### 查看完整文档
```
USER_MODULE_COMPLETE.md
```

### 运行测试
```bash
python test_user_api.py
```

### 访问API文档
```
http://127.0.0.1:8000/api/
```

### 访问后台管理
```
http://127.0.0.1:8000/admin/
```

---

**最后更新**: 2026-01-25
**版本**: v1.0.0
