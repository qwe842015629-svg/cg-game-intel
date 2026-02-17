# 翻译API集成文档

## 概述

本项目已集成翻译之家（trans-home.com）的翻译API服务，提供以下功能：
- 单文本翻译
- 批量翻译
- 多语种翻译（一次性翻译成多种语言）
- 翻译统计信息查询

## API密钥

- **密钥**: `mnnwBJkNAlkt7UHWxqo2`
- **API地址**: `http://www.trans-home.com`

## 后端接口

### 1. 单文本翻译
```
POST /api/translate/
Content-Type: application/json

{
  "text": "Hello, world!",
  "targetLanguage": "zh-CN",
  "sourceLanguage": "en"  // 可选
}

Response:
{
  "success": true,
  "translatedText": "你好，世界！",
  "message": "翻译成功"
}
```

### 2. 批量翻译
```
POST /api/translate/batch/
Content-Type: application/json

{
  "texts": ["Hello", "World", "Good morning"],
  "targetLanguage": "ja"
}

Response:
{
  "success": true,
  "translatedTexts": ["こんにちは", "世界", "おはよう"],
  "message": "批量翻译成功"
}
```

### 3. 多语种翻译
```
POST /api/translate/multi/
Content-Type: application/json

{
  "text": "Welcome",
  "targetLanguages": ["zh-CN", "ja", "ko"]
}

Response:
{
  "success": true,
  "translations": {
    "zh": "欢迎",
    "ja": "ようこそ",
    "ko": "환영합니다"
  },
  "message": "多语种翻译成功"
}
```

### 4. 获取支持的语言列表
```
GET /api/translate/languages/

Response:
{
  "success": true,
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English"
    },
    ...
  ]
}
```

### 5. 获取翻译统计信息
```
GET /api/translate/stats/

Response:
{
  "success": true,
  "available": 10000,
  "used": 200,
  "message": "获取成功"
}
```

## 前端使用

### 导入翻译服务
```typescript
import {
  translateText,
  translateBatch,
  translateMultiLanguage,
  getSupportedLanguages,
  getTranslationStats
} from '@/services/translationApi'
```

### 单文本翻译
```typescript
const result = await translateText('Hello', 'zh-CN')
console.log(result) // "你好"
```

### 批量翻译
```typescript
const results = await translateBatch(
  ['Hello', 'World'],
  'ja'
)
console.log(results) // ["こんにちは", "世界"]
```

### 多语种翻译
```typescript
const translations = await translateMultiLanguage(
  'Welcome',
  ['zh-CN', 'ja', 'ko']
)
console.log(translations)
// {
//   "zh": "欢迎",
//   "ja": "ようこそ",
//   "ko": "환영합니다"
// }
```

## 支持的语言

| 代码 | 语言 | 本地名称 |
|------|------|----------|
| en | English | English |
| ja | Japanese | 日本語 |
| ko | Korean | 한국어 |
| th | Thai | ไทย |
| vi | Vietnamese | Tiếng Việt |
| zh-CN | Chinese Simplified | 简体中文 |
| zh-TW | Chinese Traditional | 繁體中文 |
| fr | French | Français |
| de | German | Deutsch |

## 翻译演示页面

访问 `/translation-demo` 路由查看完整的翻译功能演示：
```
http://localhost:5177/translation-demo
```

演示页面包含：
- 单文本翻译测试
- 批量翻译测试
- 多语种翻译测试
- 翻译额度统计显示

## 使用建议

1. **批量翻译优化**: 如果需要翻译多个文本，使用批量翻译接口可以减少请求次数
2. **缓存翻译结果**: 对于常用文本，建议缓存翻译结果以节省API额度
3. **错误处理**: 所有API调用都应该包含错误处理逻辑
4. **额度监控**: 定期查询翻译统计信息，避免额度耗尽

## 自动翻译locales

如果需要自动翻译locales配置文件：

```typescript
import { autoTranslateLocales } from '@/services/translationApi'

// 原始英文文本
const englishTexts = {
  home: 'Home',
  games: 'Games',
  recharge: 'Recharge',
  // ...
}

// 自动翻译成日文
const japaneseTexts = await autoTranslateLocales(englishTexts, 'ja')
console.log(japaneseTexts)
// {
//   home: 'ホーム',
//   games: 'ゲーム',
//   recharge: 'チャージ',
//   // ...
// }
```

## 注意事项

1. API密钥已硬编码在 `translation_service.py` 中，生产环境建议使用环境变量
2. 翻译服务依赖外部API，需要确保服务器可以访问 trans-home.com
3. 注意翻译字符数限制，避免超出可用额度
4. 翻译结果可能因API引擎而略有差异

## 文件结构

```
main/
├── translation_service.py      # 翻译服务类
└── translation_views.py        # Django视图

frontend/src/
├── services/
│   └── translationApi.ts      # 前端API服务
└── views/
    └── TranslationDemo.vue    # 翻译演示页面
```

## 故障排查

### 翻译请求失败
1. 检查后端服务是否运行
2. 检查API密钥是否正确
3. 检查网络连接是否正常
4. 查看浏览器控制台错误信息

### 跨域问题
确保Django设置中已配置CORS：
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5177",
]
```

## 技术支持

如有问题，请参考官方文档：
- 翻译之家API文档: https://www.trans-home.com/index/index/api
