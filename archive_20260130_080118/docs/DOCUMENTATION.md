# 游戏充值网站 - 完整文档

> **最后更新**: 2026-01-29  
> **版本**: v1.0.0

---

## 📚 目录

1. [项目简介](#项目简介)
2. [技术架构](#技术架构)
3. [快速开始](#快速开始)
4. [功能模块](#功能模块)
5. [API文档](#api文档)
6. [数据库设计](#数据库设计)
7. [开发指南](#开发指南)
8. [部署运维](#部署运维)
9. [常见问题](#常见问题)

---

## 项目简介

### 🎯 项目概述

这是一个基于 **Django 5.1.5 + Vue 3** 的全栈游戏充值网站项目，提供多种游戏的充值服务、游戏资讯、用户管理等功能。

### ✨ 核心功能

- ✅ **游戏商品管理**：游戏分类、游戏信息、充值商品
- ✅ **资讯系统**：文章发布、分类管理、评论互动
- ✅ **用户系统**：注册登录、个人中心、邮件激活
- ✅ **轮播图管理**：首页Banner、活动推广
- ✅ **多语言支持**：中文、英文、日文、韩文、泰文、越南文等
- ✅ **后台管理**：SimpleUI美化的Django Admin

### 🛠 技术栈

**后端**:
- Django 5.1.5 + Django REST Framework 3.16.1
- MySQL 数据库
- Djoser (用户认证)
- django-cors-headers (跨域支持)
- Simple UI (后台美化)

**前端**:
- Vue 3.5.13 + TypeScript
- Vite 7.3.1
- Vue Router 4 + Pinia
- Tailwind CSS v3
- Axios + vue-i18n

---

## 技术架构

### 系统架构图

```
┌─────────────────┐      ┌─────────────────┐
│   前端 (Vue 3)   │ <──> │   后端 (Django)  │
│                 │ HTTP │                 │
│  - 用户界面     │      │  - REST API     │
│  - 状态管理     │      │  - 业务逻辑     │
│  - 路由控制     │      │  - 数据管理     │
└─────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   MySQL 数据库   │
                         └─────────────────┘
```

### 项目结构

```
游戏充值网站/
├── frontend/                   # Vue 3 前端项目
│   ├── src/
│   │   ├── api/               # API服务层
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia状态管理
│   │   ├── i18n/              # 多语言配置
│   │   └── types/             # TypeScript类型
│   └── package.json
│
├── game_product/               # 游戏商品模块
│   ├── models.py              # 游戏、商品数据模型
│   ├── serializers.py         # API序列化器
│   ├── views.py               # API视图
│   └── admin.py               # 后台管理
│
├── game_article/               # 游戏资讯模块
│   ├── models.py              # 文章、评论数据模型
│   ├── serializers.py         # API序列化器
│   ├── views.py               # API视图
│   └── admin.py               # 后台管理
│
├── main/                       # 主应用模块
│   ├── models.py              # Banner等通用模型
│   ├── views.py               # 主页等视图
│   └── translation_service.py # 翻译服务
│
├── users/                      # 用户模块
│   ├── models.py              # 用户扩展模型
│   ├── serializers.py         # 用户序列化器
│   └── views.py               # 用户视图
│
├── game_recharge/              # Django项目配置
│   ├── settings.py            # 项目设置
│   ├── urls.py                # 路由配置
│   └── wsgi.py                # WSGI配置
│
├── manage.py                   # Django管理脚本
├── requirements.txt            # Python依赖
└── DOCUMENTATION.md            # 本文档
```

---

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- MySQL 8.0+

### 后端启动

```bash
# 1. 克隆项目
cd "e:\小程序开发\游戏充值网站"

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
# 编辑 .env 文件，设置数据库连接信息

# 5. 执行迁移
python manage.py migrate

# 6. 创建超级用户
python manage.py createsuperuser

# 7. 添加测试数据（可选）
python add_test_data.py

# 8. 启动服务
python manage.py runserver
```

访问：
- 后台管理：http://127.0.0.1:8000/admin/
- API接口：http://127.0.0.1:8000/api/

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

访问：http://localhost:5176/

---

## 功能模块

### 1. 游戏商品模块

**功能**：
- 游戏分类管理（国际服、港澳台、东南亚等）
- 游戏信息管理（名称、图标、封面、描述）
- 充值商品管理（价格、库存、折扣）
- 商品类型管理（点券、会员、道具、礼包）

**API端点**：
- `GET /api/products/categories/` - 获取游戏分类
- `GET /api/products/games/` - 获取游戏列表
- `GET /api/products/games/{id}/` - 获取游戏详情
- `GET /api/products/products/` - 获取充值商品列表

### 2. 游戏资讯模块

**功能**：
- 文章分类管理
- 文章发布（富文本编辑器）
- 评论系统（支持回复）
- 点赞功能
- 浏览统计

**API端点**：
- `GET /api/articles/` - 获取文章列表
- `GET /api/articles/{id}/` - 获取文章详情
- `POST /api/articles/{id}/like/` - 点赞文章
- `GET /api/articles/hot/` - 获取热门文章
- `POST /api/articles/comments/` - 发表评论

### 3. 用户系统

**功能**：
- 用户注册（邮箱验证）
- 用户登录/登出
- 个人信息管理
- 头像上传
- 密码修改
- JWT认证

**API端点**：
- `POST /auth/users/` - 用户注册
- `POST /auth/jwt/create/` - 登录获取Token
- `POST /auth/jwt/refresh/` - 刷新Token
- `GET /auth/users/me/` - 获取当前用户信息
- `POST /auth/users/activation/` - 激活账号

### 4. 轮播图管理

**功能**：
- 首页Banner管理
- 图片上传
- 链接配置
- 多语言标题
- 显示顺序

**API端点**：
- `GET /api/banners/` - 获取轮播图列表

### 5. 多语言系统

**支持语言**：
- 中文简体 (zh-CN)
- 中文繁体 (zh-TW)
- 英文 (en)
- 日文 (ja)
- 韩文 (ko)
- 泰文 (th)
- 越南文 (vi)
- 德文 (de)
- 法文 (fr)

**实现方式**：
- 前端：vue-i18n
- 后端：Google Translate API（自动翻译）

---

## API文档

### 基础信息

**Base URL**: `http://127.0.0.1:8000/api/`

**认证方式**: JWT Bearer Token

```
Authorization: Bearer {access_token}
```

### 游戏商品API

#### 获取游戏分类列表

```http
GET /api/products/categories/
```

**响应示例**：
```json
[
  {
    "id": 1,
    "name": "国际服游戏",
    "code": "international",
    "icon": "/media/icons/international.png",
    "sort_order": 1,
    "is_active": true
  }
]
```

#### 获取游戏列表

```http
GET /api/products/games/
```

**查询参数**：
- `category` - 按分类筛选
- `search` - 搜索游戏名称
- `is_hot` - 是否热门
- `page` - 页码
- `page_size` - 每页数量

**响应示例**：
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "原神",
      "name_en": "Genshin Impact",
      "description": "开放世界冒险游戏",
      "icon": "/media/games/genshin.png",
      "cover": "/media/games/genshin_cover.png",
      "category": {
        "id": 1,
        "name": "国际服游戏"
      },
      "is_hot": true,
      "tags": ["RPG", "开放世界"],
      "view_count": 1500
    }
  ]
}
```

#### 获取游戏详情

```http
GET /api/products/games/{id}/
```

**响应示例**：
```json
{
  "id": 1,
  "name": "原神",
  "name_en": "Genshin Impact",
  "description": "开放世界冒险游戏",
  "icon": "/media/games/genshin.png",
  "cover": "/media/games/genshin_cover.png",
  "category": {
    "id": 1,
    "name": "国际服游戏"
  },
  "tags": ["RPG", "开放世界"],
  "regions": ["国服", "国际服"],
  "payment_methods": ["支付宝", "微信支付"],
  "instructions": "选择区服和充值金额...",
  "recharge_options": [
    {
      "id": 1,
      "name": "60创世结晶",
      "amount": 60,
      "current_price": "6.00",
      "original_price": "6.00",
      "discount": null
    }
  ],
  "is_hot": true,
  "view_count": 1500
}
```

### 文章资讯API

#### 获取文章列表

```http
GET /api/articles/
```

**查询参数**：
- `category` - 按分类筛选
- `game` - 按游戏筛选
- `search` - 搜索标题/内容
- `ordering` - 排序 (`-created_at`, `-view_count`, `-like_count`)

**响应示例**：
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "title": "原神3.5版本更新内容",
      "slug": "genshin-3-5-update",
      "cover_image": "/media/articles/cover.jpg",
      "excerpt": "新角色、新剧情...",
      "category": {
        "id": 1,
        "name": "游戏资讯"
      },
      "author_name": "编辑部",
      "view_count": 500,
      "like_count": 50,
      "comment_count": 10,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### 用户认证API

#### 用户注册

```http
POST /auth/users/
```

**请求体**：
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123",
  "re_password": "SecurePass123"
}
```

#### 用户登录

```http
POST /auth/jwt/create/
```

**请求体**：
```json
{
  "username": "testuser",
  "password": "SecurePass123"
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 数据库设计

### 核心数据表

#### GameCategory (游戏分类)
```sql
CREATE TABLE game_category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    icon VARCHAR(200),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### Game (游戏)
```sql
CREATE TABLE game (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    description TEXT,
    icon VARCHAR(200),
    cover VARCHAR(200),
    tags JSON,
    regions JSON,
    payment_methods JSON,
    instructions TEXT,
    is_hot BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    sort_order INT DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (category_id) REFERENCES game_category(id)
);
```

#### Product (充值商品)
```sql
CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    game_id INT,
    product_type_id INT,
    name VARCHAR(200) NOT NULL,
    amount INT,
    description TEXT,
    current_price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    discount DECIMAL(5, 2),
    stock INT DEFAULT 0,
    sales_count INT DEFAULT 0,
    is_hot BOOLEAN DEFAULT FALSE,
    is_recommended BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (product_type_id) REFERENCES product_type(id)
);
```

#### Article (文章)
```sql
CREATE TABLE article (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT,
    game_id INT,
    author_id INT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE,
    cover_image VARCHAR(200),
    excerpt TEXT,
    content LONGTEXT,
    status VARCHAR(20) DEFAULT 'draft',
    is_top BOOLEAN DEFAULT FALSE,
    is_hot BOOLEAN DEFAULT FALSE,
    is_recommended BOOLEAN DEFAULT FALSE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    published_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (category_id) REFERENCES article_category(id),
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (author_id) REFERENCES auth_user(id)
);
```

---

## 开发指南

### 前端开发

#### 1. 组件开发规范

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Game } from '@/types'
import { getGames } from '@/api/games'

const games = ref<Game[]>([])

onMounted(async () => {
  try {
    const data = await getGames()
    games.value = data
  } catch (error) {
    console.error('获取游戏列表失败:', error)
  }
})
</script>

<template>
  <div class="game-list">
    <div v-for="game in games" :key="game.id" class="game-item">
      {{ game.name }}
    </div>
  </div>
</template>

<style scoped>
.game-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
</style>
```

#### 2. API调用规范

```typescript
// src/api/games.ts
import client from './client'
import type { Game, GameCategory } from '@/types'

export const getGames = async (params?: any): Promise<Game[]> => {
  const response = await client.get('/products/games/', { params })
  return response.data.results || response.data
}

export const getGameDetail = async (id: number): Promise<Game> => {
  const response = await client.get(`/products/games/${id}/`)
  return response.data
}
```

#### 3. 状态管理规范

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const login = async (credentials: any) => {
    // 登录逻辑
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, login, logout }
})
```

### 后端开发

#### 1. 模型开发规范

```python
from django.db import models

class Game(models.Model):
    """游戏模型"""
    name = models.CharField('游戏名称', max_length=200)
    name_en = models.CharField('英文名称', max_length=200, blank=True)
    category = models.ForeignKey(
        GameCategory,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name='游戏分类'
    )
    
    class Meta:
        verbose_name = '游戏'
        verbose_name_plural = '游戏'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

#### 2. 序列化器规范

```python
from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Game
        fields = ['id', 'name', 'name_en', 'category', 'category_name', 'icon']
    
    def to_representation(self, instance):
        """自定义输出格式"""
        data = super().to_representation(instance)
        # 处理图片URL
        if instance.icon:
            data['icon'] = instance.icon.url
        return data
```

#### 3. 视图开发规范

```python
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """游戏视图集"""
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'name_en']
    ordering_fields = ['created_at', 'view_count']
    
    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门游戏"""
        hot_games = self.queryset.filter(is_hot=True)[:10]
        serializer = self.get_serializer(hot_games, many=True)
        return Response(serializer.data)
```

---

## 部署运维

### 开发环境

```bash
# 后端
python manage.py runserver

# 前端
npm run dev
```

### 生产环境部署

#### 1. 后端部署 (Nginx + Gunicorn)

```bash
# 安装Gunicorn
pip install gunicorn

# 启动Gunicorn
gunicorn game_recharge.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

**Nginx配置**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/static/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. 前端部署

```bash
# 构建生产版本
npm run build

# 生成dist目录，配置Nginx指向该目录
```

---

## 常见问题

### 1. CORS跨域问题

**问题**：前端请求后端API时出现CORS错误

**解决**：检查 `settings.py` 中的CORS配置

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5176",
]
```

### 2. 数据库迁移问题

**问题**：执行迁移时出错

**解决**：
```bash
# 查看迁移状态
python manage.py showmigrations

# 清除迁移并重新创建
python manage.py migrate --fake-initial
```

### 3. 静态文件404

**问题**：静态文件无法访问

**解决**：
```bash
# 收集静态文件
python manage.py collectstatic

# 检查settings.py配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

### 4. JWT Token过期

**问题**：Token过期导致请求失败

**解决**：使用refresh token刷新access token

```typescript
// 在axios拦截器中自动刷新
client.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // 刷新token逻辑
    }
    return Promise.reject(error)
  }
)
```

---

## 📞 联系与支持

- **项目地址**: e:\小程序开发\游戏充值网站
- **开发服务器**: http://127.0.0.1:8000
- **前端地址**: http://localhost:5176
- **管理后台**: http://127.0.0.1:8000/admin/

---

## 📝 更新日志

### v1.0.0 (2026-01-29)
- ✅ 整合所有项目文档
- ✅ 完善API文档
- ✅ 添加开发指南
- ✅ 优化项目结构

### v0.9.0 (2026-01-26)
- ✅ 完成前后端集成
- ✅ 实现多语言支持
- ✅ 添加轮播图功能
- ✅ 用户邮件激活

### v0.5.0 (2026-01-20)
- ✅ 游戏商品模块
- ✅ 文章资讯模块
- ✅ 用户认证系统
- ✅ 后台管理系统

---

**许可证**: MIT License
