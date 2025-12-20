export interface ApiFileItem {
  name: string;
  size: number;
  is_dir: boolean;
  last_modified: string;
}

export interface ApiFileTreeData {
  path: string;
  items: ApiFileItem[];
}

export interface ApiFileTreeResponse {
  success: boolean;
  data: ApiFileTreeData;
  message: string;
  timestamp: string;
  status_code: number;
}
