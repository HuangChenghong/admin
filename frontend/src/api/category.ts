import { get, post, type ApiResponse } from './index'

// 搜索的参数类型
type keyword = {
  name?: string
  page?: number
  pageSize?: number
}

type Category = {
  id?: number
  name: string
  description?: string
  create_at?: string
  update_at?: string
}

type AddCategory = {
  name: string
  description?: string
}

type UpdateCategory = {
  id: number
  name: string
  description?: string
}
export const getCategories = (data: keyword) => {
  return get<Category[]>('/api/category', data)
}

export const createCategory = (data: AddCategory) => {
  return post<string>('/api/category', data)   
}

export const updateCategory = (data: UpdateCategory) => {
  return post<string>('/api/update', data)
}

export const deleteCategory = (id: number) => {
  return get<string>(`/api/delCategory/${id}`) 
}
