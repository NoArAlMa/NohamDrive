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
    };
  }
}
