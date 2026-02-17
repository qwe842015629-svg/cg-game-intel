export interface RechargeGame {
  id: string;
  name: string;
  nameEn: string;
  image: string;
  category: 'international' | 'hongkong-taiwan' | 'southeast-asia';
  categoryName: string;
  hot: boolean;
  tags: string[];
  description: string;
  paymentMethods: ('alipay' | 'wechat' | 'paypal' | 'usdt' | 'foreign-currency')[];
  rechargeOptions: {
    id: string;
    amount: string;
    price: number;
    originalPrice?: number;
    discount?: number;
    popular?: boolean;
  }[];
  instructions: string[];
  processingTime: string;
  region: string[];
}

export const rechargeGames: RechargeGame[] = [
  {
    id: '1',
    name: '原神',
    nameEn: 'Genshin Impact',
    image: 'https://images.unsplash.com/photo-1639656333010-b6a054423b63?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2JpbGUlMjBnYW1lfGVufDF8fHx8MTc2OTQxNTY3NHww&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'international',
    categoryName: '国际游戏',
    hot: true,
    tags: ['RPG', '开放世界', '热门'],
    description: '米哈游旗下开放世界冒险游戏，提供创世结晶充值服务',
    paymentMethods: ['alipay', 'wechat', 'paypal', 'usdt'],
    rechargeOptions: [
      { id: '1-1', amount: '60创世结晶', price: 6, popular: false },
      { id: '1-2', amount: '300创世结晶', price: 30, popular: false },
      { id: '1-3', amount: '980创世结晶', price: 98, originalPrice: 128, discount: 23, popular: true },
      { id: '1-4', amount: '1980创世结晶', price: 198, originalPrice: 258, discount: 23 },
      { id: '1-5', amount: '3280创世结晶', price: 328, originalPrice: 428, discount: 23 },
      { id: '1-6', amount: '6480创世结晶', price: 648, originalPrice: 848, discount: 24 },
    ],
    instructions: [
      '请确认您的游戏UID正确',
      '选择对应的服务器区域',
      '充值后1-5分钟内到账',
      '如遇问题请联系客服',
    ],
    processingTime: '1-5分钟',
    region: ['国服', '美服', '欧服', '亚服'],
  },
  {
    id: '2',
    name: '王者荣耀',
    nameEn: 'Honor of Kings',
    image: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxvbmxpbmUlMjBnYW1pbmd8ZW58MXx8fHwxNzY5NDM4NTc4fDA&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'hongkong-taiwan',
    categoryName: '港台游戏',
    hot: true,
    tags: ['MOBA', '竞技', '热门'],
    description: '腾讯旗下5V5英雄公平对战手游，提供点券充值服务',
    paymentMethods: ['alipay', 'wechat', 'foreign-currency'],
    rechargeOptions: [
      { id: '2-1', amount: '60点券', price: 6 },
      { id: '2-2', amount: '300点券', price: 30 },
      { id: '2-3', amount: '588点券', price: 58, popular: true },
      { id: '2-4', amount: '1188点券', price: 118 },
      { id: '2-5', amount: '2388点券', price: 238 },
      { id: '2-6', amount: '4888点券', price: 488 },
    ],
    instructions: [
      '仅支持QQ或微信登录账号',
      '请提供正确的游戏ID',
      '充值后即时到账',
      '港台服需要选择对应区服',
    ],
    processingTime: '即时到账',
    region: ['国服', '港服', '台服'],
  },
  {
    id: '3',
    name: 'Mobile Legends',
    nameEn: 'Mobile Legends',
    image: 'https://images.unsplash.com/photo-1759701546668-4fe410517caf?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxlc3BvcnRzJTIwZ2FtZXxlbnwxfHx8fDE3Njk0Mzg1Nzl8MA&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'southeast-asia',
    categoryName: '东南亚游戏',
    hot: true,
    tags: ['MOBA', '东南亚', '热门'],
    description: '东南亚最受欢迎的MOBA手游，提供钻石充值服务',
    paymentMethods: ['alipay', 'wechat', 'paypal', 'usdt', 'foreign-currency'],
    rechargeOptions: [
      { id: '3-1', amount: '86钻石', price: 12 },
      { id: '3-2', amount: '172钻石', price: 24 },
      { id: '3-3', amount: '429钻石', price: 58, popular: true },
      { id: '3-4', amount: '878钻石', price: 118 },
      { id: '3-5', amount: '2195钻石', price: 298 },
      { id: '3-6', amount: '4649钻石', price: 628 },
    ],
    instructions: [
      '请提供游戏ID和服务器',
      '支持所有东南亚服务器',
      '充值后5-10分钟到账',
      '首次充值请核对信息',
    ],
    processingTime: '5-10分钟',
    region: ['印尼服', '马来服', '新加坡服', '菲律宾服', '泰国服'],
  },
  {
    id: '4',
    name: '和平精英',
    nameEn: 'Game for Peace',
    image: 'https://images.unsplash.com/photo-1545579003-84eeef98a485?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnB1bmslMjBnYW1lfGVufDF8fHx8MTc2OTMxNjU3Mnww&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'international',
    categoryName: '国际游戏',
    hot: true,
    tags: ['射击', '战术竞技'],
    description: '腾讯旗下战术竞技手游，提供点券充值服务',
    paymentMethods: ['alipay', 'wechat'],
    rechargeOptions: [
      { id: '4-1', amount: '60点券', price: 6 },
      { id: '4-2', amount: '300点券', price: 30 },
      { id: '4-3', amount: '680点券', price: 68, popular: true },
      { id: '4-4', amount: '1280点券', price: 128 },
      { id: '4-5', amount: '3280点券', price: 328 },
      { id: '4-6', amount: '6480点券', price: 648 },
    ],
    instructions: [
      '仅支持QQ或微信登录账号',
      '请确认游戏昵称和ID',
      '充值后即时到账',
      '如遇延迟请联系客服',
    ],
    processingTime: '即时到账',
    region: ['国服'],
  },
  {
    id: '5',
    name: 'Free Fire',
    nameEn: 'Free Fire',
    image: 'https://images.unsplash.com/photo-1659480140212-090e6e576080?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmYW50YXN5JTIwZ2FtZXxlbnwxfHx8fDE3Njk0MzY4MDl8MA&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'southeast-asia',
    categoryName: '东南亚游戏',
    hot: true,
    tags: ['射击', '东南亚'],
    description: '东南亚热门生存射击游戏，提供钻石充值服务',
    paymentMethods: ['alipay', 'wechat', 'paypal', 'foreign-currency'],
    rechargeOptions: [
      { id: '5-1', amount: '100钻石', price: 15 },
      { id: '5-2', amount: '310钻石', price: 45 },
      { id: '5-3', amount: '520钻石', price: 75, popular: true },
      { id: '5-4', amount: '1060钻石', price: 148 },
      { id: '5-5', amount: '2180钻石', price: 298 },
      { id: '5-6', amount: '5600钻石', price: 748 },
    ],
    instructions: [
      '提供Free Fire游戏ID',
      '选择正确的服务器区域',
      '充值后10分钟内到账',
      '请勿在游戏内操作',
    ],
    processingTime: '10分钟内',
    region: ['印尼服', '巴西服', '印度服', '泰国服'],
  },
  {
    id: '6',
    name: 'PUBG Mobile',
    nameEn: 'PUBG Mobile',
    image: 'https://images.unsplash.com/photo-1602940819863-2905852243ad?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyYWNpbmclMjBnYW1lfGVufDF8fHx8MTc2OTQwMDc0OHww&ixlib=rb-4.1.0&q=80&w=1080',
    category: 'international',
    categoryName: '国际游戏',
    hot: false,
    tags: ['射击', '战术竞技'],
    description: '国际版吃鸡手游，提供UC充值服务',
    paymentMethods: ['alipay', 'wechat', 'paypal', 'usdt'],
    rechargeOptions: [
      { id: '6-1', amount: '60UC', price: 8 },
      { id: '6-2', amount: '325UC', price: 38 },
      { id: '6-3', amount: '660UC', price: 78, popular: true },
      { id: '6-4', amount: '1800UC', price: 198 },
      { id: '6-5', amount: '3850UC', price: 428 },
      { id: '6-6', amount: '8100UC', price: 888 },
    ],
    instructions: [
      '请提供游戏ID',
      '支持全球服务器',
      '充值后5-15分钟到账',
      '节假日可能延迟',
    ],
    processingTime: '5-15分钟',
    region: ['全球服', '韩服', '日服'],
  },
];

export const gameCategories = [
  { id: 'all', name: '全部游戏', icon: '🎮' },
  { id: 'international', name: '国际游戏', icon: '🌍' },
  { id: 'hongkong-taiwan', name: '港台游戏', icon: '🏮' },
  { id: 'southeast-asia', name: '东南亚游戏', icon: '🌴' },
];

export const paymentMethodLabels: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信支付',
  paypal: 'PayPal',
  usdt: 'USDT',
  'foreign-currency': '外币支付',
};
