import http from './http'
import type {
  UserCreateRequest,
  UserRequestInput,
  UserRequestOutput,
  InviteTokenInfo,
  UserRegisterInput,
  UserRegisterOutput,
  User,
} from '@/types/api'

/** 直接注册（开放注册，绕过审批） */
export async function directRegister(data: UserCreateRequest): Promise<User> {
  const res = await http.post<User>('/user/', data)
  return res.data
}

/** 提交注册申请 */
export async function submitRequest(data: UserRequestInput): Promise<UserRequestOutput> {
  const res = await http.post<UserRequestOutput>('/user/request', data)
  return res.data
}

/** 通过邀请 token 完成注册 */
export async function completeRegister(data: UserRegisterInput): Promise<UserRegisterOutput> {
  const res = await http.post<UserRegisterOutput>('/user/register', data)
  return res.data
}

/** 查询邀请 token 信息 */
export async function getInviteInfo(token: string): Promise<InviteTokenInfo> {
  const res = await http.get<InviteTokenInfo>('/user/invite-info', {
    params: { token },
  })
  return res.data
}
