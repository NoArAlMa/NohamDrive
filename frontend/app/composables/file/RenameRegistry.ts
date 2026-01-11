const registry = new Map<string, () => void>();

export function useFileRenameRegistry() {
  function register(key: string, fn: () => void) {
    registry.set(key, fn);
  }

  function unregister(key: string) {
    registry.delete(key);
  }

  function start(key: string) {
    registry.get(key)?.();
  }

  return { register, unregister, start };
}
