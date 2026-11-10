import { get, post, type ApiResponse } from './index'

// 搜索的参数类型
type keyword = {
  name?: string
  page?: number
  page_size?: number
  title?: string
  category_id?: number
  status?: number | string
}

type Article = {
  id?: number
  name: string
  description?: string
  create_at?: string
  update_at?: string
  title: string
}

type AddCategory = {
  name: string
  description?: string
}

type UpdateCategory = {
  id: number
  name?: string
  status?: number
  description?: string
}
export const getArticles = (data: keyword) => {
  return get<ApiResponse<Article>>('/api/articles', data)
}

// export const createArticle = (data: AddCategory) => {
//   return post<string>('/api/article', data)   
// }

export const updateArticle = (data: UpdateCategory) => {
  return post('/api/update', data)
}

export const deleteArticle = (id: number) => {
  return get(`/api/delArticle/${id}`) 
}
