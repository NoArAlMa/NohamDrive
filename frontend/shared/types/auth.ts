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
