import { get, post, type ApiResponse } from './index'

export type CommentStatus = 0 | 1 | 2  // 0: 待审核, 1: 已通过, 2: 已拒绝

export type CommentItem = {
  id: number
  article_id: number
  article_title?: string
  user_id: number
  username?: string
  avatar?: string
  content: string
  parent_id?: number
  reply_to_user_id?: number
  reply_to_username?: string
  status: CommentStatus
  like_count: number
  create_at: string
}

type CommentQuery = {
  keyword?: string
  article_id?: number
  status?: CommentStatus | null
  start_date?: string
  end_date?: string
  page?: number
  pageSize?: number
}

type CommentReply = {
  article_id: number
  parent_id: number
  content: string
}

export const getComments = (params: CommentQuery) => {
  return post<CommentItem[]>('/api/comment/list', params)
}

export const approveComment = (id: number) => {
  return post<void>(`/api/comment/approve/${id}`, {})
}

export const rejectComment = (id: number) => {
  return post<void>(`/api/comment/reject/${id}`, {})
}

export const deleteComment = (id: number) => {
  return get<void>(`/api/delComment/${id}`)
}

export const replyComment = (data: CommentReply) => {
  return post<string>('/api/comment/reply', data)
}

export const batchDeleteComments = (ids: number[]) => {
  return post<void>('/api/comment/batchDelete', { ids })
}
