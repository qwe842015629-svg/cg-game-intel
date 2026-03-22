import client from './client'

export interface UserProfilePayload {
  id: number
  username: string
  email: string
  name: string
  first_name: string
  last_name: string
  phone: string
  gender: string
  bio: string
  avatar_url: string
  sandbox_namespace: string
  sandbox_enabled: boolean
  ai_content_visibility: 'private' | 'members' | 'public'
  global_ai_visibility: 0 | 1 | 2
  ai_isolation_mode: 'strict' | 'balanced' | string
  balance: string
  points: number
  vip_level: number
  created_at: string
  updated_at: string
}

export interface UserDashboardPayload {
  profile: UserProfilePayload
  stats: {
    novel_draft_count: number
    novel_work_count: number
    role_card_count: number
    ai_content_count: number
  }
  novel_drafts: Array<{
    id: number
    title: string
    updated_at: string
    created_at: string
    state_key_count: number
    state_keys: string[]
  }>
  novel_works: Array<{
    id: number
    title: string
    summary: string
    cover_image: string
    chapter_count: number
    character_image_count: number
    completion_status: string
    updated_at: string
    created_at: string
  }>
  role_cards: Array<{
    id: number
    post_id: number
    name: string
    description: string
    avatar: string
    gender: string
    group: string
    source_ref: string
    updated_at: string
    created_at: string
  }>
  ai_contents: Array<{
    id: number
    type: string
    content: string
    source_ref: string
    updated_at: string
    created_at: string
  }>
  sandbox: {
    enabled: boolean
    namespace: string
    isolation_mode: string
    visibility: string
    owner_scope: string
    policies: string[]
  }
}

export interface ProfileUpdatePayload {
  name?: string
  first_name?: string
  last_name?: string
  phone?: string
  gender?: string
  bio?: string
  sandbox_enabled?: boolean
  ai_content_visibility?: 'private' | 'members' | 'public'
  global_ai_visibility?: 0 | 1 | 2
  remove_avatar?: boolean
}

export type ContentVisibility = 0 | 1 | 2

export interface PublicProfileUserPayload {
  id: number
  username: string
  name: string
  avatar_url: string
  bio: string
  global_ai_visibility: ContentVisibility
}

export interface PublicProfileNovelPayload {
  id: number
  title: string
  summary: string
  cover_image: string
  visibility: ContentVisibility
  created_at: string
  updated_at: string
}

export interface PublicProfileCharacterPayload {
  id: number
  name: string
  description: string
  avatar: string
  source_ref: string
  visibility: ContentVisibility
  created_at: string
  updated_at: string
}

export interface PublicProfileCharacterDetailPayload {
  id: number
  post_id: number
  user_id: number
  name: string
  description: string
  content: string
  avatar: string
  group: string
  gender: string
  first_message: string
  source_ref: string
  visibility: ContentVisibility
  created_at: string
  updated_at: string
}

export interface PublicProfileNovelChapterPayload {
  chapter_no: number
  title: string
  content: string
}

export interface PublicProfileNovelDetailPayload {
  id: number
  user_id: number
  title: string
  summary: string
  cover_image: string
  visibility: ContentVisibility
  completion_status: string
  chapter_count: number
  chapters: PublicProfileNovelChapterPayload[]
  created_at: string
  updated_at: string
}

export interface PublicUserProfilePayload {
  user: PublicProfileUserPayload
  follower_count: number
  following_count: number
  is_owner: boolean
  is_following: boolean
  novels: PublicProfileNovelPayload[]
  characters: PublicProfileCharacterPayload[]
}

export interface FollowStatePayload {
  target_user_id: number
  is_following: boolean
  follower_count: number
  following_count: number
}

export type UserRelationMode = 'followers' | 'following'

export interface UserRelationItemPayload {
  id: number
  username: string
  name: string
  avatar_url: string
  bio: string
  followed_at: string
}

export interface UserRelationListPayload {
  user_id: number
  mode: UserRelationMode
  total: number
  items: UserRelationItemPayload[]
}

export interface DirectMessageInitPayload {
  created: boolean
  thread: {
    id: number
    initiator: number
    recipient: number
    created_at: string
    updated_at: string
  }
}

export interface DirectMessagePayload {
  id: number
  thread: number
  sender: number
  sender_name: string
  sender_avatar_url: string
  content: string
  created_at: string
  updated_at: string
}

export interface DirectMessageThreadSummaryPayload {
  thread: {
    id: number
    initiator: number
    recipient: number
    created_at: string
    updated_at: string
  }
  peer: {
    id: number
    username: string
    name: string
    avatar_url: string
  }
  last_message: DirectMessagePayload | null
  unread_count: number
}

export interface DirectMessageThreadListPayload {
  threads: DirectMessageThreadSummaryPayload[]
  total_unread_threads: number
  total_unread_messages: number
}

export interface DirectMessageThreadMessagesPayload {
  thread: {
    id: number
    initiator: number
    recipient: number
    created_at: string
    updated_at: string
  }
  messages: DirectMessagePayload[]
}

export const fetchMyProfile = async (): Promise<UserProfilePayload> => {
  return await client.get('/users/me/profile/')
}

export const fetchMyDashboard = async (limit = 20): Promise<UserDashboardPayload> => {
  return await client.get('/users/me/dashboard/', {
    params: {
      limit,
    },
  })
}

export const updateMyProfile = async (payload: ProfileUpdatePayload): Promise<UserProfilePayload> => {
  return await client.patch('/users/me/profile/', payload)
}

export const updateMyProfileWithAvatar = async (
  payload: ProfileUpdatePayload,
  avatarFile: File
): Promise<UserProfilePayload> => {
  const formData = new FormData()

  Object.entries(payload).forEach(([key, value]) => {
    if (typeof value === 'undefined' || value === null) return
    formData.append(key, String(value))
  })
  formData.append('avatar', avatarFile)

  return await client.patch('/users/me/profile/', formData)
}

export const fetchUserPublicProfile = async (userId: number | string): Promise<PublicUserProfilePayload> => {
  return await client.get(`/users/${userId}/profile/`)
}

export const fetchUserPublicNovelDetail = async (
  userId: number | string,
  novelId: number | string
): Promise<PublicProfileNovelDetailPayload> => {
  return await client.get(`/users/${userId}/novels/${novelId}/`)
}

export const fetchUserPublicCharacterDetail = async (
  userId: number | string,
  characterId: number | string
): Promise<PublicProfileCharacterDetailPayload> => {
  return await client.get(`/users/${userId}/characters/${characterId}/`)
}

export const fetchUserFollowState = async (userId: number | string): Promise<FollowStatePayload> => {
  return await client.get(`/users/${userId}/follow/`)
}

export const followUser = async (userId: number | string): Promise<FollowStatePayload> => {
  return await client.post(`/users/${userId}/follow/`)
}

export const unfollowUser = async (userId: number | string): Promise<FollowStatePayload> => {
  return await client.delete(`/users/${userId}/follow/`)
}

export const fetchUserRelationList = async (
  userId: number | string,
  mode: UserRelationMode,
  limit = 100
): Promise<UserRelationListPayload> => {
  return await client.get(`/users/${userId}/${mode}/`, {
    params: { limit },
  })
}

export const initDirectMessage = async (userId: number | string): Promise<DirectMessageInitPayload> => {
  return await client.post(`/users/${userId}/dm/init/`)
}

export const fetchDirectMessageThreads = async (limit = 30): Promise<DirectMessageThreadListPayload> => {
  return await client.get('/users/dm/threads/', {
    params: { limit },
  })
}

export const fetchDirectMessageThreadMessages = async (
  threadId: number | string,
  limit = 60,
  markRead = false
): Promise<DirectMessageThreadMessagesPayload> => {
  return await client.get(`/users/dm/threads/${threadId}/messages/`, {
    params: {
      limit,
      ...(markRead ? { mark_read: 1 } : {}),
    },
  })
}

export const sendDirectMessage = async (
  threadId: number | string,
  content: string
): Promise<DirectMessagePayload> => {
  return await client.post(`/users/dm/threads/${threadId}/messages/`, { content })
}

export const markDirectMessageThreadRead = async (
  threadId: number | string
): Promise<{ thread_id: number; last_read_message_id: number; unread_count: number }> => {
  return await client.post(`/users/dm/threads/${threadId}/read/`)
}

export const updateNovelVisibility = async (
  novelId: number | string,
  visibility: ContentVisibility
): Promise<PublicProfileNovelPayload> => {
  return await client.patch(`/novel-works/${novelId}/`, { visibility })
}

export const updateCharacterVisibility = async (
  characterId: number | string,
  visibility: ContentVisibility
): Promise<any> => {
  return await client.patch(`/plaza-posts/${characterId}/`, { visibility })
}
