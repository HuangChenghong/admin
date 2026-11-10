import { get ,post} from './index'

type LogQuery = {
  log_type?: string
  oper_username?: string
  page?: number
  pageSize?: number
  log_level?: string
  start_time?: string
  end_time?: string
}
// export type LogItem = {
//   id: number
//   log_type: string
//   log_level: string
//   oper_username: string
//   oper_ip: string
//   oper_location: string
//   oper_method: string
//   oper_params: string
//   oper_result: string
//   oper_time: string
// }


export const getLogs = (params: LogQuery) => {
  return get('/api/log', params)
}

// 导出，设置响应头为流式下载
export const exportLogs = (params: any) => {
  return post('/api/export', params, {
    responseType: 'blob'
  })
}

