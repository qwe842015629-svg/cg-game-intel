<template>
  <div class="article-list">
    <div class="container">
      <h1>游戏资讯</h1>
      
      <div class="articles">
        <div 
          v-for="article in articles" 
          :key="article.id"
          class="article-card"
          @click="goToDetail(article.id)"
        >
          <h3>{{ article.title }}</h3>
          <p>{{ article.summary }}</p>
          <div class="meta">
            <span>👁 {{ article.view_count }}</span>
            <span>👍 {{ article.like_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { articleAPI } from '@/api'

const router = useRouter()
const articles = ref([])

onMounted(async () => {
  try {
    const data = await articleAPI.getArticles()
    articles.value = data.results || data
  } catch (error) {
    console.error('加载文章失败:', error)
  }
})

const goToDetail = (id) => {
  router.push(`/article/${id}`)
}
</script>

<style scoped>
.article-list {
  min-height: 80vh;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.articles {
  display: grid;
  gap: 1rem;
}

.article-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.article-card:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.article-card h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.article-card p {
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.meta {
  display: flex;
  gap: 1.5rem;
  color: #95a5a6;
  font-size: 0.9rem;
}
</style>
