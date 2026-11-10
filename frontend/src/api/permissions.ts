import { get, post, type ApiResponse } from './index'

export type PermType = 'menu' | 'button' | 'api'

export type PermItem = {
  id: number
  name: string
  code: string
  type: PermType
  icon?: string
  path?: string
  component?: string
  sort: number
  status: 0 | 1
  parent_id: number
  remark?: string
  created_at: string
  children?: PermItem[]
}

type PermCreate = Omit<PermItem, 'id' | 'created_at' | 'children'>
type PermUpdate = PermCreate & { id: number }

export const getPermissionTree = () => {
  return get<PermItem[]>('/api/permission/tree')
}

export const createPermission = (data: PermCreate) => {
  return post<string>('/api/permission', data)
}

export const updatePermission = (data: PermUpdate) => {
  return post<string>('/api/permission/update', data)
}

export const deletePermission = (id: number) => {
  return get<void>(`/api/delPermission/${id}`)
}
