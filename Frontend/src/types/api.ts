export type UserRole = 'user' | 'admin'

export interface User {
  id: number
  email: string
  created_at: string
  role: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserCreateRequest {
  email: string
  password: string
}

export interface UserRequestInput {
  email: string
  reason: string
}

export interface UserRequestOutput {
  id: number
  email: string
  reason: string | null
  status: string | null
}

export interface InviteTokenInfo {
  email: string
  expired: boolean
  used: boolean
}

export interface UserRegisterInput {
  token: string
  password: string
}

export interface UserRegisterOutput {
  id: number
  email: string
  created_at: string
}

export interface ApproveResponse {
  message: string
  email: string
  register_url: string
}
