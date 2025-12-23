export interface RenameFilePayload {
  path: string;
  new_name: string;
}

export interface CopyFilePayload {
  source_path: string;
  destination_folder: string;
}

export interface UploadFilePayload {
  path: string;
}
