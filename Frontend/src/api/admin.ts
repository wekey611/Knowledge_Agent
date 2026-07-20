import http from './http'
import type { UserRequestOutput, ApproveResponse } from '@/types/api'

/** 获取所有注册申请（管理员） */
export async function getRequests(): Promise<UserRequestOutput[]> {
  const res = await http.get<UserRequestOutput[]>('/admin/requests')
  return res.data
}

/** 审批注册申请 */
export async function approveRequest(requestId: number): Promise<ApproveResponse> {
  const res = await http.post<ApproveResponse>(`/admin/${requestId}/approve`)
  return res.data
}
