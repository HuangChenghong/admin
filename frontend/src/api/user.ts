import { get, post } from './index'

type registerData = {
    username: string
    email: string
    password: string
    confirmPassword: string
}

export type loginData = {
    username: string
    password: string
}
export type loginResponse = {
    access_token: string
    username: string
    refresh_token: string
    user_id?: number
    // role: string
    // status: number
}

// 登录/刷新成功时顶层字段必选（实际业务逻辑在 code===200 时使用）
export type loginSuccessResponse = loginResponse & {
    code: number
    msg: string
}



export const getHome = () => {
    return get('/api/home')
}
export const register = (data: registerData) => {
    return post('/api/register', data)
}
export const login = (data: loginData) => {
    return post('/api/login', data) as Promise<loginSuccessResponse>
}
export const logout = () => {
    return get('/api/logout')
}

export const getUser = (data: any) => {
    return post('/api/user', data)
}
export const forbiddenUser = (id: number) => {
    return get(`/api/forbidden/${id}`)
}
export const activeUser = (id: number) => {
    return get(`/api/active/${id}`)
}

export const deleteUser = (id: number) => {
    return get(`/api/delete/${id}`)
}

// 管理员后台：新增用户 / 编辑用户
export const adminCreateUser = (data: any) => {
    return post('/api/createUser', data)
}
export const adminUpdateUser = (id: number, data: any) => {
    return post(`/api/updateUser/${id}`, data)
}



