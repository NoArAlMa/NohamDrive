export interface UserCreatePayload {
  name: string;
  password: string;
  username: string;
  email: string;
}

export interface UserLoginPayload {
  email: string;
  password: string;
}

export interface Token {
  token: string;
  expiration_date: Date;
  creation_date: Date;
  scope: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  creation_date: Date;
}

export interface AuthUserResponse {
  user: User;
  token: Token;
}

export type AuthResponse<T = any> = {
  success: boolean;
  data?: T;
  fieldErrors?: { name: string; message: string }[];
  message?: string;
  statusCode?: number;
};
