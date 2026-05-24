export {};

declare global {
  interface Window {
    electronAPI?: {
      // Info de l'app
      getAppInfo: () => Promise<{
        isElectron: boolean;
        appVersion: string;
        platform: string;
        arch: string;
      }>;
      getRuntime: () => Promise<{
        host: string;
        port: string;
        token: string;
        started_at: string;
      }>;
      selectFolder: () => Promise<string | null>;
      onSyncStateUpdated: (status) => Promise<>;
    };
  }
}
