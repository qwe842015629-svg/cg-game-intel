<template>
  <div class="game-detail">
    <div class="container">
      <div v-if="game" class="detail-content">
        <h1>{{ game.name }}</h1>
        <p class="developer">开发商：{{ game.developer }}</p>
        <p class="description">{{ game.description }}</p>
        
        <div class="products-section">
          <h2>充值商品</h2>
          <div class="products-grid">
            <div 
              v-for="product in products" 
              :key="product.id"
              class="product-card"
            >
              <h3>{{ product.name }}</h3>
              <p class="price">¥{{ product.current_price }}</p>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="loading">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { gameAPI, productAPI } from '@/api'

const route = useRoute()
const game = ref(null)
const products = ref([])

onMounted(async () => {
  const gameId = route.params.id
  try {
    game.value = await gameAPI.getGameDetail(gameId)
    const data = await productAPI.getProducts({ game: gameId })
    products.value = data.results || data
  } catch (error) {
    console.error('加载详情失败:', error)
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

.developer {
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.description {
  line-height: 1.8;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.products-section {
  margin-top: 2rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.product-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.price {
  color: #e74c3c;
  font-size: 1.5rem;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 4rem;
}
</style>
