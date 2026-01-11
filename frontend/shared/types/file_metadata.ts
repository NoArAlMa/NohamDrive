export interface FileMetadata {
  nom: string;
  taille_octets: number;
  taille_ko: number;
  type_mime: string;
  date_modification: string;
  chemin: string;
  etag: number;
  version_id: number;
  nombre_fichiers: number;
}
