export interface GenericAPIResponse<T> {
  success: boolean;
  data: T | null;
  timestamp: string;
  message: string;
  status_code: number;
}
