export interface FileMetadata {
  // ----- Base -----
  name: string;
  path: string;
  content_type: string;
  last_modified?: string;

  // ----- File -----
  size_bytes?: number;
  size_kb?: number;
  etag?: string;
  version_id?: string;

  // ----- Image -----
  width?: number;
  height?: number;
  format?: string;

  // ----- Video -----
  duration?: number;
  codec?: string;
  fps?: number;

  // ----- Folder -----
  file_count?: number;

  // ----- Type discriminant -----
  file_type: "file" | "image" | "video" | "folder";
}
