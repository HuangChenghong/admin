import { get, post, type ApiResponse } from './index'

export type RoleItem = {
  id: number
  role_name: string
  role_code: string
  remark?: string
  status: 0 | 1
  user_count?: number
  permission_ids?: number[]
  created_at: string
  updated_at: string
}

type RoleQuery = {
  role_name?: string
  status?: 0 | 1 | null
  page?: number
  pageSize?: number
}

type RoleCreate = {
  role_name: string
  role_code: string
  remark?: string
  status?: 0 | 1
  permission_ids?: number[]
}

type RoleUpdate = {
  id: number
  role_name: string
  role_code: string
  remark?: string
  status?: 0 | 1
  permission_ids?: number[]
}

export type PermissionItem = {
  id: number
  name: string
  code: string
  type: 'menu' | 'button'
  parent_id: number
  children?: PermissionItem[]
}

export const getRoles = (params: RoleQuery) => {
  return get<RoleItem[]>('/api/roles', params)
}

export const createRole = (data: RoleCreate) => {
  return post('/api/role', data)
}

export const updateRole = (data: RoleUpdate) => {
  return post('/api/updateRole', data)
}

export const deleteRole = (id: number) => {
  return get(`/api/delRole/${id}`)
}

export const getPermissions = (): Promise<ApiResponse<PermissionItem[]>> => {
  return get<PermissionItem[]>('/api/permissions')
}
