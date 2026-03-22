import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { LoginCredentials, RegisterData, User } from '../types'
import client from '../api/client'
import { fetchMyProfile, type UserProfilePayload } from '../api/profile'

const normalizeText = (value: unknown) => String(value || '').trim()

const mapProfileToUser = (profile: UserProfilePayload): User => ({
  id: profile.id,
  username: profile.username,
  name: normalizeText(profile.name) || normalizeText(profile.username) || '匿名用户',
  email: normalizeText(profile.email),
  avatar: normalizeText(profile.avatar_url),
  gender: normalizeText(profile.gender),
  bio: normalizeText(profile.bio),
  phone: normalizeText(profile.phone),
  sandboxEnabled: Boolean(profile.sandbox_enabled),
  aiContentVisibility: profile.ai_content_visibility,
})

const mapLegacyMeToUser = (payload: any): User => ({
  id: payload?.id,
  username: normalizeText(payload?.username),
  name: normalizeText(payload?.name) || normalizeText(payload?.username) || '匿名用户',
  email: normalizeText(payload?.email),
  avatar:
    normalizeText(payload?.avatar_url) ||
    `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(normalizeText(payload?.email) || 'user')}`,
  gender: normalizeText(payload?.gender),
  bio: normalizeText(payload?.bio),
})

type LoginAttemptPayload = {
  email?: string
  username?: string
  password: string
}

const buildLoginAttemptPayloads = (credentials: LoginCredentials): LoginAttemptPayload[] => {
  const identity = normalizeText(credentials?.email)
  const normalizedEmail = identity.toLowerCase()
  const password = String(credentials?.password ?? '')

  const attempts: LoginAttemptPayload[] = []
  const seen = new Set<string>()

  const pushUnique = (payload: LoginAttemptPayload) => {
    const key = JSON.stringify(payload)
    if (seen.has(key)) return
    seen.add(key)
    attempts.push(payload)
  }

  if (!normalizedEmail) {
    pushUnique({ password })
    return attempts
  }

  // Preferred: backend LOGIN_FIELD=email.
  pushUnique({ email: normalizedEmail, password })
  // Compatibility: some deployed environments still use username login.
  pushUnique({ username: normalizedEmail, password })

  if (normalizedEmail.includes('@')) {
    const prefix = normalizedEmail.split('@', 1)[0]
    if (prefix) {
      pushUnique({ username: prefix, password })
    }
  }

  return attempts
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => user.value !== null)

  const persistUser = () => {
    if (user.value) {
      localStorage.setItem('user', JSON.stringify(user.value))
    } else {
      localStorage.removeItem('user')
    }
  }

  const setUser = (nextUser: User | null) => {
    user.value = nextUser
    persistUser()
  }

  const applyProfilePayload = (profile: UserProfilePayload) => {
    const mapped = mapProfileToUser(profile)
    setUser(mapped)
  }

  const refreshUser = async () => {
    const profile = await fetchMyProfile()
    applyProfilePayload(profile)
    return profile
  }

  const login = async (credentials: LoginCredentials) => {
    const attempts = buildLoginAttemptPayloads(credentials)
    let lastError: any = null

    for (const payload of attempts) {
      try {
        const response: any = await client.post('/auth/token/login/', payload)
        localStorage.setItem('authToken', response.auth_token)

        try {
          await refreshUser()
          return
        } catch (error) {
          // Fallback to legacy me endpoint for compatibility.
          const userResponse: any = await client.get('/auth/users/me/', {
            headers: {
              Authorization: `Token ${response.auth_token}`,
            },
          })
          setUser(mapLegacyMeToUser(userResponse))
          return
        }
      } catch (error: any) {
        lastError = error
        const status = Number(error?.response?.status || 0)
        // Stop retrying when backend/service is unavailable.
        if (!status || status >= 500) {
          break
        }
      }
    }

    throw lastError || new Error('Login failed')
  }

  const register = async (data: RegisterData) => {
    await client.post('/auth/users/', {
      username: data.name,
      email: data.email,
      password: data.password,
      re_password: data.confirmPassword,
    })
  }

  const logout = async () => {
    const token = localStorage.getItem('authToken')
    if (token) {
      try {
        await client.post(
          '/auth/token/logout/',
          {},
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        )
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    setUser(null)
    localStorage.removeItem('authToken')
    localStorage.removeItem('token')
  }

  const init = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        user.value = null
      }
    }

    const token = localStorage.getItem('authToken') || localStorage.getItem('token')
    if (token) {
      refreshUser().catch((error) => {
        console.warn('refresh user failed:', error)
      })
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    init,
    refreshUser,
    setUser,
    applyProfilePayload,
  }
})
