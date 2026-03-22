import client from './client'

export interface ChatKnowledgeItem {
  id: number
  title?: string
  question?: string
  answer?: string
  category?: string
  slug?: string | null
}

export interface ChatKnowledgeResponse {
  faqs: ChatKnowledgeItem[]
  games: ChatKnowledgeItem[]
  articles: ChatKnowledgeItem[]
  agent: {
    name: string
    show_knowledge_panel: boolean
    transfer_keywords: string[]
  }
}

export interface ChatMessage {
  id: number
  sender_type: 'user' | 'ai' | 'agent' | 'system'
  sender_type_display: string
  sender_name: string
  content: string
  metadata: Record<string, any>
  created_at: string
}

export interface ChatSession {
  session_id: string
  status: 'ai' | 'human' | 'closed'
  status_display: string
  visitor_name: string
  is_user_waiting: boolean
  assigned_agent_name: string
  created_at: string
  updated_at: string
}

export interface InitChatSessionResponse {
  created: boolean
  visitor_token: string
  session: ChatSession
  messages: ChatMessage[]
}

export interface ChatMessagesResponse {
  session: ChatSession
  messages: ChatMessage[]
  server_time: string
}

export interface ChatSendResponse {
  handoff: boolean
  session: ChatSession
  messages: ChatMessage[]
}

export const getChatKnowledge = async (): Promise<ChatKnowledgeResponse> => {
  return (await client.get('/customer-service/chat/knowledge/')) as ChatKnowledgeResponse
}

export const initChatSession = async (payload: {
  visitor_token?: string
  visitor_name?: string
  visitor_contact?: string
  source_page?: string
  session_id?: string
}): Promise<InitChatSessionResponse> => {
  return (await client.post('/customer-service/chat/session/init/', payload)) as InitChatSessionResponse
}

export const getChatMessages = async (params: {
  sessionId: string
  visitorToken?: string
  sinceId?: number
}): Promise<ChatMessagesResponse> => {
  const query: Record<string, string | number> = {}
  if (params.visitorToken) query.visitor_token = params.visitorToken
  if (params.sinceId && params.sinceId > 0) query.since_id = params.sinceId
  return (await client.get(`/customer-service/chat/session/${params.sessionId}/messages/`, { params: query })) as ChatMessagesResponse
}

export const sendChatMessage = async (params: {
  sessionId: string
  content: string
  visitorToken?: string
}): Promise<ChatSendResponse> => {
  return (await client.post(`/customer-service/chat/session/${params.sessionId}/send/`, {
    content: params.content,
    visitor_token: params.visitorToken,
  })) as ChatSendResponse
}

export const handoffChatToHuman = async (params: {
  sessionId: string
  visitorToken?: string
}): Promise<{ session: ChatSession }> => {
  return (await client.post(`/customer-service/chat/session/${params.sessionId}/handoff/`, {
    visitor_token: params.visitorToken,
  })) as { session: ChatSession }
}

export const resumeChatToAi = async (params: {
  sessionId: string
  visitorToken?: string
}): Promise<{ session: ChatSession; messages: ChatMessage[] }> => {
  return (await client.post(`/customer-service/chat/session/${params.sessionId}/resume-ai/`, {
    visitor_token: params.visitorToken,
  })) as { session: ChatSession; messages: ChatMessage[] }
}
