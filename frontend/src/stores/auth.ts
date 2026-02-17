import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData } from '../types'
import client from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => user.value !== null)

  // Djoser login function
  const login = async (credentials: LoginCredentials) => {
    const response: any = await client.post('/auth/token/login/', credentials)
    
    // Save auth token
    localStorage.setItem('authToken', response.auth_token)
    
    // Get user info
    const userResponse: any = await client.get('/auth/users/me/', {
      headers: {
        Authorization: `Token ${response.auth_token}`
      }
    })
    
    user.value = {
      id: userResponse.id,
      name: userResponse.username,
      email: userResponse.email,
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + userResponse.email,
    }
    
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  // Djoser register function
  const register = async (data: RegisterData) => {
    await client.post('/auth/users/', {
      username: data.name,
      email: data.email,
      password: data.password,
      re_password: data.confirmPassword
    })
    
    // Don't set user here - they need to activate via email first
    // Registration success will be handled by AuthDialog component
  }

  const logout = async () => {
    const token = localStorage.getItem('authToken')
    if (token) {
      try {
        await client.post('/auth/token/logout/', {}, {
          headers: {
            Authorization: `Token ${token}`
          }
        })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('authToken')
  }

  // Initialize from localStorage
  const init = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    init,
  }
})
