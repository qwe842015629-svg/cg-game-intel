# MySQL 数据库配置指南

## 前提条件

确保您已经安装了 MySQL 服务器。

### Windows 安装 MySQL
1. 下载 MySQL Community Server: https://dev.mysql.com/downloads/mysql/
2. 运行安装程序
3. 记住设置的 root 密码

### 检查 MySQL 是否运行
```bash
# Windows
mysql --version

# 或检查服务是否运行
Get-Service MySQL*
```

---

## 步骤 1: 创建数据库

### 方法一：使用 MySQL 命令行

```bash
# 登录 MySQL
mysql -u root -p

# 输入密码后，创建数据库
CREATE DATABASE game_recharge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建专用用户（可选，推荐）
CREATE USER 'game_user'@'localhost' IDENTIFIED BY 'your_secure_password';

# 授予权限
GRANT ALL PRIVILEGES ON game_recharge.* TO 'game_user'@'localhost';

# 刷新权限
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 方法二：使用图形化工具

**使用 MySQL Workbench** 或 **Navicat** 或 **phpMyAdmin**：
1. 连接到 MySQL 服务器
2. 创建新数据库：`game_recharge`
3. 字符集选择：`utf8mb4`
4. 排序规则：`utf8mb4_unicode_ci`

---

## 步骤 2: 配置环境变量

编辑 `.env` 文件，更新以下配置：

```env
# 数据库配置（MySQL）
DB_ENGINE=mysql
DB_NAME=game_recharge
DB_USER=root              # 或您创建的用户名
DB_PASSWORD=your_password  # 您的MySQL密码
DB_HOST=localhost
DB_PORT=3306
```

**重要提示**：
- 请将 `your_password` 替换为您的实际 MySQL 密码
- 如果创建了专用用户，请使用该用户名和密码
- 确保 `.env` 文件在 `.gitignore` 中（已配置）

---

## 步骤 3: 执行数据库迁移

```bash
# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 执行迁移
python manage.py migrate
```

### 预期输出
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, game_article, game_product, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## 步骤 4: 创建超级用户

```bash
python manage.py createsuperuser
```

---

## 步骤 5: 生成测试数据（可选）

```bash
python create_test_data.py
```

---

## 步骤 6: 启动服务器

```bash
python manage.py runserver
```

---

## 常见问题解决

### 问题 1: mysqlclient 安装失败

**错误信息**: `error: Microsoft Visual C++ 14.0 or greater is required`

**解决方案**:
```bash
# 方案 1: 安装预编译版本
pip install mysqlclient-2.2.7-cp313-cp313-win_amd64.whl

# 方案 2: 使用 pymysql 替代
pip uninstall mysqlclient
pip install pymysql

# 然后在 settings.py 顶部添加
import pymysql
pymysql.install_as_MySQLdb()
```

### 问题 2: 连接被拒绝

**错误信息**: `Can't connect to MySQL server on 'localhost'`

**解决方案**:
1. 检查 MySQL 服务是否运行
   ```bash
   Get-Service MySQL*
   ```
2. 如果未运行，启动服务
   ```bash
   Start-Service MySQL80  # 服务名可能不同
   ```

### 问题 3: 认证失败

**错误信息**: `Access denied for user 'root'@'localhost'`

**解决方案**:
1. 检查密码是否正确
2. 检查用户是否存在且有权限
3. 尝试重置 MySQL root 密码

### 问题 4: 字符集问题

**错误信息**: 中文乱码

**解决方案**:
```sql
-- 检查数据库字符集
SHOW CREATE DATABASE game_recharge;

-- 如果不是 utf8mb4，修改
ALTER DATABASE game_recharge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题 5: 端口被占用

**错误信息**: `Port 3306 is already in use`

**解决方案**:
1. 检查是否有其他 MySQL 实例运行
2. 修改 `.env` 中的 `DB_PORT` 为其他端口
3. 或停止其他 MySQL 实例

---

## 数据迁移（从 SQLite 到 MySQL）

如果您之前使用 SQLite 并有数据需要迁移：

### 方法一：使用 Django 命令

```bash
# 1. 导出现有数据
python manage.py dumpdata > data.json

# 2. 切换到 MySQL 配置

# 3. 执行迁移
python manage.py migrate

# 4. 导入数据
python manage.py loaddata data.json
```

### 方法二：重新生成测试数据

```bash
# 直接运行测试数据脚本
python create_test_data.py
```

---

## MySQL 优化建议

### 1. 连接池配置（生产环境）

在 `settings.py` 中添加：
```python
DATABASES = {
    'default': {
        # ... 其他配置
        'CONN_MAX_AGE': 600,  # 连接池最大生命周期（秒）
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,  # 连接超时
        },
    }
}
```

### 2. 性能优化

```sql
-- 为常用查询添加索引
ALTER TABLE game_product_game ADD INDEX idx_is_hot (is_hot);
ALTER TABLE game_product_product ADD INDEX idx_game_id (game_id);
ALTER TABLE game_article_article ADD INDEX idx_status (status);
```

### 3. 备份配置

```bash
# 定期备份数据库
mysqldump -u root -p game_recharge > backup_$(date +%Y%m%d).sql

# 恢复备份
mysql -u root -p game_recharge < backup_20260126.sql
```

---

## 验证配置

运行以下命令验证配置：

```bash
# 测试数据库连接
python manage.py dbshell

# 查看数据库配置
python manage.py showmigrations

# 运行 API 测试
python test_api.py
```

---

## 配置检查清单

- [ ] MySQL 服务已安装并运行
- [ ] 数据库 `game_recharge` 已创建
- [ ] `.env` 文件已正确配置
- [ ] mysqlclient 已安装
- [ ] 数据库迁移已执行
- [ ] 超级用户已创建
- [ ] 测试数据已生成
- [ ] 开发服务器可正常启动
- [ ] API 接口测试通过

---

## 技术支持

如遇到问题，请检查：
1. MySQL 错误日志
2. Django 开发服务器日志
3. `.env` 文件配置
4. 防火墙设置

MySQL 日志位置（Windows）：
```
C:\ProgramData\MySQL\MySQL Server 8.0\Data\
```
