<template>
  <div class="game-list">
    <div class="container">
      <h1>游戏列表</h1>
      
      <div class="filters">
        <input 
          v-model="searchText" 
          type="text" 
          placeholder="搜索游戏..." 
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="games">
        <div 
          v-for="game in games" 
          :key="game.id"
          class="game-card"
          @click="goToDetail(game.id)"
        >
          <div class="game-icon">🎮</div>
          <h3>{{ game.name }}</h3>
          <p>{{ game.category_name }}</p>
          <span v-if="game.is_hot" class="badge">HOT</span>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gameAPI } from '@/api'

const router = useRouter()
const games = ref([])
const searchText = ref('')
const loading = ref(false)

onMounted(async () => {
  await loadGames()
})

const loadGames = async () => {
  loading.value = true
  try {
    const data = await gameAPI.getGames({ search: searchText.value })
    games.value = data.results || data
  } catch (error) {
    console.error('加载游戏失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadGames()
}

const goToDetail = (id) => {
  router.push(`/game/${id}`)
}
</script>

<style scoped>
.game-list {
  min-height: 80vh;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.filters {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  max-width: 500px;
  padding: 0.75rem 1rem;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 1rem;
}

.games {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.game-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.game-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #e74c3c;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}
</style>
