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

export interface CompressFilePayload {
  objects: string[];
  destination_folder: string;
  output_base_name?: string;
}

export interface CreateFolderPayload {
  currentPath: string;
  folderPath: string;
}
