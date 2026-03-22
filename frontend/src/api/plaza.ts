import client from './client'

export type PlazaPostType = 'text' | 'role_card' | 'novel_work'

export interface PlazaComment {
  id: number
  post: number
  owner_key: string
  author_id: number | null
  author_name: string
  author_avatar: string
  content: string
  created_at: string
  updated_at: string
  is_owner: boolean
}

export interface PlazaPost {
  id: number
  owner_key: string
  author_id: number | null
  author_name: string
  author_avatar: string
  content: string
  post_type: PlazaPostType
  source_ref: string
  source_data: Record<string, any>
  like_count: number
  comment_count: number
  comments: PlazaComment[]
  liked_by_me: boolean
  is_owner: boolean
  created_at: string
  updated_at: string
}

export interface CreatePlazaPostPayload {
  client_id: string
  author_name?: string
  author_avatar?: string
  content: string
  post_type: PlazaPostType
  source_ref?: string
  source_data?: Record<string, any>
}

export interface CreatePlazaCommentPayload {
  client_id: string
  author_name?: string
  author_avatar?: string
  content: string
}

const PLAZA_CLIENT_KEY = 'plaza_client_id'

const randomClientId = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID().replace(/-/g, '').slice(0, 32)
  }
  return `${Date.now()}${Math.random().toString(36).slice(2, 12)}`
}

export const ensurePlazaClientId = () => {
  let clientId = ''
  try {
    clientId = String(localStorage.getItem(PLAZA_CLIENT_KEY) || '').trim()
    if (!clientId) {
      clientId = randomClientId()
      localStorage.setItem(PLAZA_CLIENT_KEY, clientId)
    }
  } catch {
    clientId = randomClientId()
  }
  return clientId.slice(0, 64)
}

export const fetchPlazaPosts = async (clientId: string): Promise<PlazaPost[]> => {
  const payload: any = await client.get('/plaza-posts/', {
    params: {
      client_id: clientId,
      include_comments: 1,
    },
  })
  return Array.isArray(payload) ? payload : []
}

export const createPlazaPost = async (payload: CreatePlazaPostPayload): Promise<PlazaPost> => {
  return await client.post('/plaza-posts/', payload)
}

export const deletePlazaPost = async (postId: number, clientId: string) => {
  return await client.delete(`/plaza-posts/${postId}/`, {
    params: { client_id: clientId },
  })
}

export const togglePlazaLike = async (postId: number, clientId: string): Promise<{ liked: boolean; like_count: number }> => {
  return await client.post(`/plaza-posts/${postId}/like/`, {
    client_id: clientId,
  })
}

export const createPlazaComment = async (postId: number, payload: CreatePlazaCommentPayload): Promise<PlazaComment> => {
  return await client.post(`/plaza-posts/${postId}/comments/`, payload)
}

export const deletePlazaComment = async (postId: number, commentId: number, clientId: string): Promise<{ comment_count: number }> => {
  return await client.delete(`/plaza-posts/${postId}/comments/${commentId}/`, {
    params: { client_id: clientId },
  })
}
