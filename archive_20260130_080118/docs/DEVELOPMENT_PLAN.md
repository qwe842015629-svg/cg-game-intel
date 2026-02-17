# 功能开发计划

## 已完成功能 ✅

### 1. 项目基础架构
- [x] Django 项目初始化
- [x] 应用模块创建（main, users, games, orders, payments, game_product, game_article）
- [x] 数据库配置
- [x] 静态文件和媒体文件配置
- [x] CORS 跨域配置
- [x] REST Framework 配置

### 2. 游戏商品模块
- [x] 游戏分类模型
- [x] 游戏信息模型
- [x] 商品类型模型
- [x] 充值商品模型
- [x] Admin 管理界面
- [x] REST API 接口
- [x] 序列化器

### 3. 游戏资讯模块
- [x] 文章分类模型
- [x] 文章模型
- [x] 文章标签模型
- [x] 评论模型
- [x] Admin 管理界面
- [x] REST API 接口
- [x] 序列化器

### 4. 测试数据
- [x] 测试数据生成脚本
- [x] 6个游戏
- [x] 13个商品
- [x] 4篇文章
- [x] 测试用户

---

## 待开发功能 ⬜

### 阶段一：用户认证系统（高优先级）

#### 1. 用户注册功能
**文件**: `users/models.py`, `users/serializers.py`, `users/views.py`

**需求**:
- 手机号注册
- 邮箱注册
- 短信验证码
- 邮箱验证码
- 用户信息完善

**API 端点**:
```
POST /api/users/register/
POST /api/users/verify-code/
POST /api/users/complete-profile/
```

**数据模型扩展**:
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)
    avatar = models.ImageField(upload_to='avatars/')
    nickname = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 2. 用户登录功能
**需求**:
- 账号密码登录
- 手机号登录
- 第三方登录（微信、QQ）
- JWT Token 认证
- 记住登录状态

**API 端点**:
```
POST /api/users/login/
POST /api/users/logout/
POST /api/users/token/refresh/
GET /api/users/me/
```

#### 3. 密码管理
**需求**:
- 修改密码
- 忘记密码
- 重置密码

**API 端点**:
```
POST /api/users/change-password/
POST /api/users/forgot-password/
POST /api/users/reset-password/
```

---

### 阶段二：订单系统（高优先级）

#### 1. 订单模型设计
**文件**: `orders/models.py`

```python
class Order(models.Model):
    """订单主表"""
    order_no = models.CharField(max_length=32, unique=True)  # 订单号
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    # 商品信息快照
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # 充值信息
    game_account = models.CharField(max_length=100)  # 游戏账号
    game_server = models.CharField(max_length=100, blank=True)  # 游戏区服
    
    # 订单状态
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('refunded', '已退款'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 金额信息
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # 时间记录
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # 备注
    remark = models.TextField(blank=True)
```

#### 2. 订单 API
**需求**:
- 创建订单
- 查询订单
- 订单列表
- 订单详情
- 取消订单

**API 端点**:
```
POST /api/orders/create/
GET /api/orders/
GET /api/orders/{id}/
POST /api/orders/{id}/cancel/
GET /api/orders/my-orders/
```

#### 3. 订单状态管理
**需求**:
- 订单状态流转
- 订单超时自动取消
- 订单完成通知
- 订单异常处理

---

### 阶段三：支付系统（高优先级）

#### 1. 支付宝支付
**文件**: `payments/alipay.py`

**需求**:
- PC端网页支付
- 手机网站支付
- APP支付
- 支付回调处理
- 支付查询

**配置**:
```python
# settings.py
ALIPAY_CONFIG = {
    'app_id': os.getenv('ALIPAY_APP_ID'),
    'app_private_key_path': 'keys/app_private_key.pem',
    'alipay_public_key_path': 'keys/alipay_public_key.pem',
    'notify_url': 'http://yourdomain.com/api/payments/alipay/notify/',
    'return_url': 'http://yourdomain.com/payment/success/',
}
```

#### 2. 微信支付
**文件**: `payments/wechat.py`

**需求**:
- JSAPI支付（公众号/小程序）
- Native支付（扫码）
- APP支付
- H5支付
- 支付回调处理
- 支付查询

**配置**:
```python
# settings.py
WECHAT_PAY_CONFIG = {
    'app_id': os.getenv('WECHAT_APP_ID'),
    'mch_id': os.getenv('WECHAT_MCH_ID'),
    'api_key': os.getenv('WECHAT_API_KEY'),
    'notify_url': 'http://yourdomain.com/api/payments/wechat/notify/',
}
```

#### 3. 支付模型
```python
class Payment(models.Model):
    """支付记录"""
    payment_no = models.CharField(max_length=32, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('balance', '余额支付'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 第三方支付信息
    trade_no = models.CharField(max_length=64, blank=True)  # 第三方交易号
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
```

#### 4. 支付 API
**API 端点**:
```
POST /api/payments/create/
POST /api/payments/alipay/notify/
POST /api/payments/wechat/notify/
GET /api/payments/query/{payment_no}/
POST /api/payments/refund/
```

---

### 阶段四：功能增强（中优先级）

#### 1. 购物车功能
**需求**:
- 添加到购物车
- 购物车列表
- 修改数量
- 删除商品
- 批量结算

#### 2. 收藏功能
**需求**:
- 收藏游戏
- 收藏商品
- 收藏文章
- 收藏列表

#### 3. 优惠券系统
**需求**:
- 优惠券发放
- 优惠券领取
- 优惠券使用
- 优惠券过期

#### 4. 积分系统
**需求**:
- 积分获取规则
- 积分消耗
- 积分兑换
- 积分记录

#### 5. 会员等级
**需求**:
- 会员等级划分
- 会员权益
- 升级规则
- 等级展示

---

### 阶段五：运营功能（中优先级）

#### 1. 轮播图管理
**需求**:
- 首页轮播图
- 分类轮播图
- 跳转链接配置
- 显示顺序

#### 2. 公告系统
**需求**:
- 系统公告
- 活动公告
- 公告弹窗
- 公告列表

#### 3. 客服系统
**需求**:
- 在线客服
- 消息通知
- 常见问题
- 反馈建议

#### 4. 统计分析
**需求**:
- 用户统计
- 订单统计
- 销售统计
- 数据报表

---

### 阶段六：优化提升（低优先级）

#### 1. 缓存优化
- Redis 缓存
- 热点数据缓存
- API 响应缓存

#### 2. 性能优化
- 数据库查询优化
- SQL 慢查询分析
- 接口性能监控

#### 3. 安全加固
- XSS 防护
- CSRF 防护
- SQL 注入防护
- 接口限流

#### 4. 搜索优化
- Elasticsearch 集成
- 全文搜索
- 搜索建议
- 搜索记录

---

## 开发时间估算

| 阶段 | 功能 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 一 | 用户认证系统 | 5-7天 | 高 |
| 二 | 订单系统 | 7-10天 | 高 |
| 三 | 支付系统 | 10-15天 | 高 |
| 四 | 功能增强 | 10-15天 | 中 |
| 五 | 运营功能 | 7-10天 | 中 |
| 六 | 优化提升 | 持续进行 | 低 |

---

## 技术选型建议

### 1. 用户认证
- **JWT**: djangorestframework-simplejwt
- **第三方登录**: python-social-auth

### 2. 短信服务
- 阿里云短信
- 腾讯云短信

### 3. 支付接口
- **支付宝**: python-alipay-sdk
- **微信支付**: wechatpy

### 4. 缓存
- Redis
- django-redis

### 5. 任务队列
- Celery
- Redis（作为broker）

### 6. 监控
- Sentry（错误监控）
- Prometheus（性能监控）

---

## 部署方案

### 开发环境
- 本地开发
- SQLite 数据库
- Django runserver

### 测试环境
- 云服务器
- MySQL/PostgreSQL
- Nginx + Gunicorn

### 生产环境
- 负载均衡
- 数据库主从
- Redis 集群
- CDN 加速
- HTTPS 证书

---

## 下一步行动

### 立即开始
1. 实现用户注册登录功能
2. 完善用户模型
3. 配置 JWT 认证

### 本周目标
1. 完成用户认证系统
2. 开始订单模块开发
3. 设计支付流程

### 本月目标
1. 完成核心功能开发
2. 前端页面开发
3. 开始测试和优化

---

## 参考文档

- [Django 官方文档](https://docs.djangoproject.com/)
- [DRF 官方文档](https://www.django-rest-framework.org/)
- [支付宝开放平台](https://opendocs.alipay.com/)
- [微信支付开发文档](https://pay.weixin.qq.com/wiki/doc/api/index.html)
- [JWT 认证](https://django-rest-framework-simplejwt.readthedocs.io/)
