# 🔧 重启Django服务器 - 解决菜单未显示问题

## ❗ 当前问题

后台管理系统中看不到"游戏页面管理"菜单，经检查发现**Django服务器使用的是旧配置**。

## ✅ 完整解决步骤

### 第1步：关闭所有Django进程

**方法A：通过命令行窗口关闭（推荐）**

1. 找到运行Django的黑色命令行窗口
2. 在窗口中按 `Ctrl + C`
3. 等待1-2秒，直到看到命令提示符：
   ```
   (venv) PS E:\小程序开发\游戏充值网站>
   ```
4. 如果没有停止，再按一次 `Ctrl + C`

**方法B：强制关闭所有Python进程**

如果方法A不起作用，使用这个命令：

```bash
# 在PowerShell中运行（会关闭所有Python进程，请先保存其他工作）
taskkill /F /IM python.exe
```

⚠️ **注意**：这会关闭所有Python程序，请确保没有其他重要的Python程序在运行。

---

### 第2步：清理临时文件（可选但推荐）

```bash
# 在项目根目录运行
cd e:\小程序开发\游戏充值网站

# 删除Python缓存文件
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
```

---

### 第3步：重新启动Django服务器

```bash
# 1. 确保在项目根目录
cd e:\小程序开发\游戏充值网站

# 2. 激活虚拟环境（如果未激活）
.\venv\Scripts\activate

# 3. 启动Django服务器
python manage.py runserver
```

**等待看到以下提示**：
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 30, 2026 - XX:XX:XX
Django version 5.1.5, using settings 'game_recharge.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ 如果看到上述信息，说明服务器启动成功！

---

### 第4步：强制刷新浏览器

1. 打开浏览器，访问：http://127.0.0.1:8000/admin/
2. 按键盘快捷键：`Ctrl + Shift + R`
3. 等待页面完全重新加载

---

### 第5步：验证菜单是否显示

在左侧菜单栏中应该能看到：

```
📄 游戏页面管理
   ├── 页面分类
   └── 游戏页面
```

**位置**：在"产品展示管理"和"用户管理"之间

---

## 🧪 验证方法

### 验证1：查看页面源代码

1. 在后台管理页面，按 `Ctrl + U` 查看源代码
2. 按 `Ctrl + F` 搜索："游戏页面管理"
3. **应该能找到**类似这样的内容：
   ```javascript
   {"app": "game_page", "name": "游戏页面管理", "icon": "fas fa-file-alt", ...}
   ```

如果**找不到**，说明服务器还是旧配置，返回第1步重新操作。

### 验证2：直接访问管理页面

在浏览器地址栏输入：
```
http://127.0.0.1:8000/admin/game_page/gamepage/
```

- ✅ **能打开** = 功能正常，只是菜单缓存问题
- ❌ **404错误** = 服务器配置有问题

---

## 📋 完整操作清单

按顺序勾选完成：

- [ ] 1. 关闭Django服务器（Ctrl+C 或 taskkill）
- [ ] 2. 清理Python缓存（可选）
- [ ] 3. 重新启动服务器（python manage.py runserver）
- [ ] 4. 等待启动成功提示
- [ ] 5. 强制刷新浏览器（Ctrl+Shift+R）
- [ ] 6. 查看左侧菜单
- [ ] 7. 验证"游戏页面管理"出现

---

## ❓ 如果还是看不到

### 检查1：确认配置文件

运行检查脚本：
```bash
python check_game_page.py
```

应该看到：
```
✓ GamePage 已注册到 Admin
✓ GamePageCategory 已注册到 Admin
```

### 检查2：查看Django启动日志

查看启动时是否有红色错误信息。常见错误：
- `ModuleNotFoundError` = 应用未正确安装
- `ImproperlyConfigured` = 配置错误

### 检查3：检查settings.py

确认 `game_page` 在 INSTALLED_APPS 中：
```python
INSTALLED_APPS = [
    # ... 其他应用 ...
    'game_page',  # ← 这一行必须存在
]
```

---

## 🚨 紧急备用方案

如果以上所有方法都不行：

### 方案1：手动重启电脑
重启电脑可以清除所有缓存和进程。

### 方案2：使用不同端口
```bash
python manage.py runserver 8001
```
然后访问：http://127.0.0.1:8001/admin/

### 方案3：清除浏览器所有数据
1. 打开浏览器设置
2. 找到"清除浏览数据"
3. 选择"所有时间"
4. 勾选所有选项
5. 清除

---

## 📞 获取帮助

如果问题仍未解决，请：

1. **截图以下内容**：
   - Django启动时的完整输出
   - 运行 `python check_game_page.py` 的结果
   - 浏览器按F12后的控制台错误
   - 页面源代码中搜索"menus"的部分

2. **查看文档**：
   - `显示游戏页面菜单-操作指南.md`
   - `GAME_PAGE_MODULE_DOC.md`

---

**预计完成时间**：3-5分钟  
**成功率**：99%

🎮 按照步骤操作，菜单一定会出现！
