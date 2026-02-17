<template>
  <div class="article-detail">
    <div class="container">
      <div v-if="article" class="detail-content">
        <h1>{{ article.title }}</h1>
        <div class="meta">
          <span>作者：{{ article.author_name }}</span>
          <span>👁 {{ article.view_count }}</span>
          <span>👍 {{ article.like_count }}</span>
        </div>
        <div class="content" v-html="article.content"></div>
      </div>
      <div v-else class="loading">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { articleAPI } from '@/api'

const route = useRoute()
const article = ref(null)

onMounted(async () => {
  const articleId = route.params.id
  try {
    article.value = await articleAPI.getArticleDetail(articleId)
  } catch (error) {
    console.error('加载文章失败:', error)
  }
})
</script>

<style scoped>
.detail-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.meta {
  display: flex;
  gap: 1.5rem;
  color: #7f8c8d;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.content {
  line-height: 1.8;
  color: #2c3e50;
  white-space: pre-wrap;
}

.loading {
  text-align: center;
  padding: 4rem;
}
</style>
