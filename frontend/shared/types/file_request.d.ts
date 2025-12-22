export interface RenameFilePayload {
  path: string;
  new_name: string;
}

export interface RenameFileResponse {
  success: boolean;
  data: any;
  message: string;
  timestamp: string;
  status_code: number;
}
