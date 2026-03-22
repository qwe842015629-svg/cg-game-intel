// 游戏相关类型
export interface RechargeOption {
  id: string
  amount: string
  price: number
  originalPrice?: number
  discount?: number
  popular?: boolean
}

export type GameCategory = 'international' | 'hongkong-taiwan' | 'southeast-asia'

export type PaymentMethod = 'alipay' | 'wechat' | 'paypal' | 'usdt' | 'foreign-currency'

export interface RechargeGame {
  id: string
  name: string
  nameEn: string
  image: string
  category: GameCategory
  categoryName: string
  hot: boolean
  tags: string[]
  description: string
  paymentMethods: PaymentMethod[]
  rechargeOptions: RechargeOption[]
  instructions: string[]
  processingTime: string
  region: string[]
}

export interface GameCategoryItem {
  id: string
  name: string
  nameKey: string
  icon: string
  code?: string  // 分类代码，用于API查询
  gamesCount?: number
}

// 文章相关类型
export interface Article {
  id: string
  title: string
  excerpt: string
  content: string
  image: string
  category: string
  author: string
  date: string
  readTime: string
  tags: string[]
}

// 用户相关类型
export interface User {
  id: number | string
  name: string
  username?: string
  email: string
  avatar?: string
  gender?: string
  bio?: string
  phone?: string
  sandboxEnabled?: boolean
  aiContentVisibility?: 'private' | 'members' | 'public' | string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
  confirmPassword?: string  // 可选，用于前端验证
}

// 评论相关类型
export interface Comment {
  id: string
  userId: string
  userName: string
  userAvatar?: string
  content: string
  createdAt: string
  rating?: number
}

// 充值问题相关类型
export interface RechargeQuestion {
  id: string
  title: string
  category: string
  content: string
  views: number
  helpful: number
  lastUpdated: string
}
