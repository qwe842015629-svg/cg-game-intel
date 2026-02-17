﻿﻿﻿<template>
  <div class="min-h-screen bg-background text-foreground pb-20">
    <div v-if="loading" class="flex justify-center items-center min-h-[60vh]">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>

    <div v-else-if="error" class="container mx-auto px-4 py-12 text-center">
      <div class="text-destructive text-xl mb-4">{{ error }}</div>
      <router-link to="/games" class="text-primary hover:underline">返回游戏列表</router-link>
    </div>

    <div v-else class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Breadcrumb -->
      <nav class="flex items-center text-sm text-muted-foreground mb-6" v-motion-reveal="{ y: 14 }">
        <router-link to="/" class="hover:text-primary transition-colors">首页</router-link>
        <span class="mx-2">/</span>
        <router-link to="/games" class="hover:text-primary transition-colors">游戏列表</router-link>
        <span class="mx-2">/</span>
        <span class="text-foreground font-medium">{{ game.title }}</span>
      </nav>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Left Content (8 cols) -->
        <div class="lg:col-span-8 space-y-8">
          
          <!-- Hero Section -->
          <div class="bg-card rounded-xl border border-border shadow-sm overflow-hidden" v-motion-reveal="{ y: 24 }">
            <!-- Banner Background (Optional, if we have a banner_image) -->
            <div v-if="game.banner_image_url" class="h-48 w-full relative">
               <div class="absolute inset-0 bg-gradient-to-t from-card to-transparent z-10"></div>
               <img :src="game.banner_image_url" class="w-full h-full object-cover opacity-80" alt="Banner">
            </div>
            
            <div class="p-6 relative z-20 flex flex-col md:flex-row gap-6" :class="{'mt-[-4rem]': game.banner_image_url}">
              <!-- Game Icon -->
              <div class="flex-shrink-0 mx-auto md:mx-0">
                <div class="w-32 h-32 md:w-40 md:h-40 rounded-xl overflow-hidden border-4 border-card shadow-lg bg-muted" v-tilt="{ max: 3.2, scale: 1.01 }">
                  <img
                    :src="getGameIconPrimary()"
                    :data-fallbacks="getGameIconFallbackData()"
                    :data-placeholder="getGameIconPlaceholder()"
                    class="w-full h-full object-cover"
                    :alt="game.title"
                    @error="handleGameImageError"
                  >
                </div>
              </div>

              <!-- Game Info -->
              <div class="flex-1 text-center md:text-left space-y-3">
                <h1 class="text-2xl md:text-3xl font-bold text-foreground">{{ game.title }}</h1>
                
                <!-- Tags/Badges -->
                <div class="flex flex-wrap justify-center md:justify-start gap-2">
                  <span v-if="game.is_hot" class="px-2 py-0.5 rounded text-xs font-medium bg-red-500/10 text-red-500 border border-red-500/20">
                    🔥 热门
                  </span>
                  <span v-if="game.is_recommended" class="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/10 text-blue-500 border border-blue-500/20">
                    ⭐ 推荐
                  </span>
                  <span class="px-2 py-0.5 rounded text-xs font-medium bg-secondary text-secondary-foreground">
                    {{ game.category_name }}
                  </span>
                </div>

                <!-- Basic Meta -->
                <div class="grid grid-cols-2 gap-x-8 gap-y-2 text-sm text-muted-foreground max-w-md mx-auto md:mx-0">
                  <div class="flex items-center gap-2">
                    <i class="fas fa-building w-4"></i>
                    <span>开发商: {{ game.developer || 'Unknown' }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="fas fa-globe w-4"></i>
                    <span>地区: {{ displayRegion }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="fas fa-mobile-alt w-4"></i>
                    <span>平台: {{ game.platform }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <i class="fas fa-server w-4"></i>
                    <span>服务器: {{ game.server_name || 'All' }}</span>
                  </div>
                </div>

                <!-- Description -->
                <p class="text-sm text-muted-foreground line-clamp-2 md:line-clamp-3">
                  {{ game.description }}
                </p>
              </div>
            </div>

            <!-- Actions Bar -->
            <div class="px-6 pb-6 pt-2 border-t border-border mt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div class="text-sm text-muted-foreground">
                <span class="text-primary font-bold">{{ game.view_count }}</span> 人正在浏览此游戏
              </div>
              <div class="flex gap-3 w-full sm:w-auto">
                <button @click="contactSupport" v-magnetic="{ strength: 0.2, max: 11 }" class="flex-1 sm:flex-none px-6 py-2.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-all font-medium shadow-md shadow-primary/20 flex items-center justify-center gap-2">
                  <i class="fas fa-comment-dots"></i> 联系客服充值
                </button>
                <button class="px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-all border border-border">
                  <i class="fas fa-share-alt"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Content Tabs -->
          <div class="bg-card rounded-xl border border-border shadow-sm overflow-hidden min-h-[500px]" v-motion-reveal="{ delay: 80, y: 22 }">
            <div class="flex border-b border-border bg-muted/30">
              <button 
                v-for="tab in tabs" 
                :key="tab.id"
                @click="currentTab = tab.id"
                class="px-6 py-4 text-sm font-medium transition-all relative"
                :class="currentTab === tab.id ? 'text-primary bg-card' : 'text-muted-foreground hover:text-foreground'"
              >
                {{ tab.label }}
                <div v-if="currentTab === tab.id" class="absolute top-0 left-0 w-full h-0.5 bg-primary"></div>
              </button>
            </div>
            
            <div class="p-6 md:p-8">
              <div v-if="currentTab === 'details'" class="prose dark:prose-invert max-w-none game-rich-content">
                <div v-html="detailsContentHtml"></div>
              </div>
              <div v-if="currentTab === 'topup'" class="prose dark:prose-invert max-w-none game-rich-content">
                <div v-html="topupContentHtml"></div>
              </div>
            </div>
          </div>

        </div>

        <!-- Right Sidebar (4 cols) -->
        <div class="lg:col-span-4 space-y-6">
          
          <!-- Service Guarantee -->
          <div class="bg-card rounded-xl border border-border p-5 shadow-sm" v-motion-reveal="{ delay: 70, y: 16 }" v-tilt="{ max: 2.8, scale: 1.004 }">
            <h3 class="font-bold text-foreground mb-4 flex items-center gap-2">
              <i class="fas fa-shield-alt text-primary"></i> 服务保障
            </h3>
            <div class="space-y-4">
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-green-500/10 flex items-center justify-center text-green-500 shrink-0">
                  <i class="fas fa-check"></i>
                </div>
                <div>
                  <div class="font-medium text-sm">官方渠道</div>
                  <div class="text-xs text-muted-foreground">所有充值均为正规官方渠道</div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500 shrink-0">
                  <i class="fas fa-bolt"></i>
                </div>
                <div>
                  <div class="font-medium text-sm">极速到账</div>
                  <div class="text-xs text-muted-foreground">下单后平均 1-10 分钟内完成</div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-purple-500/10 flex items-center justify-center text-purple-500 shrink-0">
                  <i class="fas fa-headset"></i>
                </div>
                <div>
                  <div class="font-medium text-sm">24/7 客服</div>
                  <div class="text-xs text-muted-foreground">全天候在线为您服务</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Contact Card -->
          <div class="bg-gradient-to-br from-primary/10 to-transparent rounded-xl border border-primary/20 p-5" v-motion-reveal="{ delay: 120, y: 16 }">
            <h3 class="font-bold text-foreground mb-2">找不到想要的商品？</h3>
            <p class="text-sm text-muted-foreground mb-4">如果您需要的充值项目不在列表中，请直接联系我们的在线客服咨询。</p>
            <button @click="contactSupport" v-magnetic="{ strength: 0.18, max: 10 }" class="w-full py-2 bg-card border border-border rounded-lg text-sm font-medium hover:bg-muted transition-colors">
              联系客服咨询
            </button>
          </div>

          <!-- Recent Updates (Mock) -->
          <div class="bg-card rounded-xl border border-border p-5 shadow-sm" v-motion-reveal="{ delay: 160, y: 16 }">
             <h3 class="font-bold text-foreground mb-4">最新公告</h3>
             <ul class="space-y-3 text-sm">
               <li class="text-muted-foreground hover:text-primary cursor-pointer truncate">• [公告] 2月4日 系统维护通知</li>
               <li class="text-muted-foreground hover:text-primary cursor-pointer truncate">• [活动] 新春充值优惠活动开启</li>
               <li class="text-muted-foreground hover:text-primary cursor-pointer truncate">• [提醒] 请勿相信非官方客服账号</li>
             </ul>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import client from '../api/client';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref('');
const game = ref<any>({});
const currentTab = ref('details');

const tabs = [
  { id: 'details', label: '游戏详情' },
  { id: 'topup', label: '充值说明' }
];

const containsHtmlTag = (value: string) => /<\/?[a-z][\s\S]*>/i.test(value);

const escapeHtml = (value: string) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

const BACKEND_ORIGIN = (() => {
  const preferred = (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim();
  if (preferred) {
    return preferred.replace(/\/+$/, '');
  }
  return 'http://127.0.0.1:8000';
})();

const resolveImageUrl = (url: string) => {
  if (url.startsWith('/media/')) {
    return `${BACKEND_ORIGIN}${url}`;
  }
  return url;
};

const getGameIconCandidates = (): string[] => {
  const unique = new Set<string>();
  const candidates = [
    game.value?.icon_image_url,
    game.value?.icon_external_url,
    game.value?.image,
    game.value?.banner_image_url,
  ];

  candidates.forEach((candidate) => {
    const value = String(candidate || '').trim();
    if (value) unique.add(value);
  });

  return Array.from(unique);
};

const buildInlineGamePlaceholder = (label: string, size: number = 240): string => {
  const safeLabel = String(label || 'GAME').slice(0, 10);
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${Math.round(size * 0.16)}" fill="#f5f5f5"/>
  <rect x="1.5" y="1.5" width="${size - 3}" height="${size - 3}" rx="${Math.round(size * 0.16) - 1}" fill="none" stroke="#e5e7eb"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="${Math.round(size * 0.1)}" font-family="Arial, sans-serif">${safeLabel}</text>
</svg>`;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
};

const getGameIconPlaceholder = (): string => {
  return buildInlineGamePlaceholder(String(game.value?.title || game.value?.name || 'GAME'), 240);
};

const getGameIconPrimary = (): string => {
  const candidates = getGameIconCandidates();
  return candidates[0] || getGameIconPlaceholder();
};

const getGameIconFallbackData = (): string => {
  const candidates = getGameIconCandidates();
  return JSON.stringify(candidates.slice(1));
};

const handleGameImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  let queue: string[] = [];

  try {
    queue = JSON.parse(img.dataset.fallbacks || '[]');
  } catch {
    queue = [];
  }

  const next = queue.shift();
  if (next) {
    img.dataset.fallbacks = JSON.stringify(queue);
    img.src = next;
    return;
  }

  const placeholder = img.dataset.placeholder || getGameIconPlaceholder();
  if (img.src !== placeholder) {
    img.src = placeholder;
    return;
  }

  img.onerror = null;
};

const sanitizeUrl = (rawUrl: string, allowRelative: boolean = true) => {
  const url = (rawUrl || '').trim();
  if (!url) return '';

  if (/^https?:\/\//i.test(url)) return url;
  if (/^mailto:/i.test(url)) return url;
  if (allowRelative && url.startsWith('/')) return url;
  return '';
};

const renderInlineMarkdown = (line: string) => {
  const tokenRegex = /!\[([^\]]*)\]\(([^)]+)\)|\[([^\]]+)\]\(([^)]+)\)/g;
  let output = '';
  let lastIndex = 0;
  let match: RegExpExecArray | null = null;

  while ((match = tokenRegex.exec(line)) !== null) {
    output += escapeHtml(line.slice(lastIndex, match.index));

    // Image token: ![alt](url)
    if (match[1] !== undefined) {
      const altText = escapeHtml(match[1] || 'image');
      const imageUrl = resolveImageUrl(sanitizeUrl(match[2] || '', true));
      if (imageUrl) {
        output += `<img class="gp-image" src="${imageUrl}" alt="${altText}" loading="lazy" />`;
      } else {
        output += escapeHtml(match[0]);
      }
    } else {
      // Link token: [text](url)
      const text = escapeHtml(match[3] || '');
      const linkUrl = sanitizeUrl(match[4] || '', true);
      if (linkUrl) {
        output += `<a class="gp-link" href="${linkUrl}" target="_blank" rel="noopener noreferrer">${text}</a>`;
      } else {
        output += escapeHtml(match[0]);
      }
    }

    lastIndex = tokenRegex.lastIndex;
  }

  output += escapeHtml(line.slice(lastIndex));
  return output;
};

const formatPlainTextToHtml = (raw: string) => {
  const normalized = raw.replace(/\r\n/g, '\n').trim();
  if (!normalized) return '';

  const blocks = normalized
    .split(/\n{2,}/)
    .map(block => block.trim())
    .filter(Boolean);

  return blocks
    .map(block => {
      if (/^【[^】]+】$/.test(block)) {
        return `<h3 class="gp-section-title">${escapeHtml(block)}</h3>`;
      }

      const content = block
        .split('\n')
        .map(line => renderInlineMarkdown(line))
        .join('<br />');

      return `<p class="gp-paragraph">${content}</p>`;
    })
    .join('');
};

const renderContent = (raw: string | undefined, emptyText: string) => {
  const value = (raw || '').trim();
  if (!value) {
    return `<p class='text-muted-foreground text-center py-8'>${emptyText}</p>`;
  }
  if (containsHtmlTag(value)) {
    return value;
  }
  return formatPlainTextToHtml(value);
};

const detailsContentHtml = computed(() => renderContent(game.value?.content, '暂无详细介绍'));
const topupContentHtml = computed(() => renderContent(game.value?.topup_info, '请联系客服获取充值说明'));

const displayRegion = computed(() => {
  const categoryLabel = String(game.value?.category_name || '').trim();
  if (categoryLabel) {
    return categoryLabel;
  }

  const rawRegion = String(game.value?.regions || '').trim();
  if (!rawRegion || /^(global|all)$/i.test(rawRegion)) {
    return '国际游戏';
  }
  if (rawRegion === '港台服' || rawRegion === '港臺服') {
    return '国际游戏';
  }

  return rawRegion;
});

const fetchGameDetails = async () => {
  const slug = route.params.id; // Assuming route param is named 'id' or 'slug'
  if (!slug) return;

  loading.value = true;
  error.value = '';

  try {
    const isId = /^\d+$/.test(slug as string);
    const response: any = isId
      ? await client.get(`/game-pages/pages/${slug}/`)
      : await client.get('/game-pages/pages/by_slug/', { params: { slug } });

    game.value = response;
    
    // Set document title
    document.title = `${game.value.title} - Cypher Game Buy`;
    
  } catch (err) {
    console.error(err);
    error.value = '加载游戏详情失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

const contactSupport = () => {
  // Logic to open chat or redirect to contact page
  router.push('/customer-service');
};

onMounted(() => {
  fetchGameDetails();
});

watch(() => route.params.id, () => {
  fetchGameDetails();
});
</script>

<style scoped>
/* Prose styles for rich text content */
:deep(.prose) {
  font-size: 0.95rem;
  line-height: 1.6;
}
:deep(.prose img) {
  border-radius: 0.5rem;
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}
:deep(.prose h2) {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: var(--foreground);
}
:deep(.prose h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--foreground);
}
:deep(.prose p) {
  margin-bottom: 1rem;
  color: var(--muted-foreground);
}
:deep(.prose ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}
:deep(.prose li) {
  color: var(--muted-foreground);
}

:deep(.game-rich-content) {
  line-height: 1.9;
}

:deep(.game-rich-content .gp-paragraph) {
  margin: 0 0 1rem;
  color: var(--foreground);
}

:deep(.game-rich-content .gp-section-title) {
  margin: 1.2rem 0 0.6rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--foreground);
}

:deep(.game-rich-content .gp-link) {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 500;
  word-break: break-word;
}

:deep(.game-rich-content .gp-link:hover) {
  opacity: 0.85;
}

:deep(.game-rich-content .gp-image) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0.85rem 0;
  border-radius: 0.55rem;
  border: 1px solid var(--border);
}
</style>

