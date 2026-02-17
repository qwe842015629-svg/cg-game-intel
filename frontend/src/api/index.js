import request from './request'

// 游戏相关API
export const gameAPI = {
  // 获取游戏分类
  getCategories() {
    return request.get('/products/categories/')
  },
  
  // 获取游戏列表
  getGames(params) {
    return request.get('/products/games/', { params })
  },
  
  // 获取游戏详情
  getGameDetail(id) {
    return request.get(`/products/games/${id}/`)
  },
  
  // 获取热门游戏
  getHotGames() {
    return request.get('/products/games/hot/')
  }
}

// 商品相关API
export const productAPI = {
  // 获取商品列表
  getProducts(params) {
    return request.get('/products/products/', { params })
  },
  
  // 获取商品详情
  getProductDetail(id) {
    return request.get(`/products/products/${id}/`)
  },
  
  // 获取热门商品
  getHotProducts() {
    return request.get('/products/products/hot/')
  }
}

// 文章相关API
export const articleAPI = {
  // 获取文章列表
  getArticles(params) {
    return request.get('/articles/articles/', { params })
  },
  
  // 获取文章详情
  getArticleDetail(id) {
    return request.get(`/articles/articles/${id}/`)
  },
  
  // 获取热门文章
  getHotArticles() {
    return request.get('/articles/articles/hot/')
  }
}
