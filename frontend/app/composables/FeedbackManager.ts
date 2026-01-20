import type { Toast } from "@nuxt/ui/runtime/composables/useToast.js";

export function useBatchAction() {
  const toast = useToast();

  let total = 0;
  let done = 0;
  let toastRef: Toast | undefined;

  function start(loadingTitle: string, count: number) {
    total = count;
    done = 0;

    toastRef = toast.add({
      title: loadingTitle,
      description: `0 / ${total}`,
      duration: 0,
      close: false,
      color: "neutral",
      ui: { icon: "animate-spin" },
      icon: "material-symbols:progress-activity",
    });
  }

  function progress() {
    done++;
    if (toastRef) {
      toast.update(toastRef.id, {
        description: `${done} / ${total}`,
      });
    }
  }

  function success(successTitle: string) {
    if (!toastRef) return;

    toast.remove(toastRef.id);
    toast.add({
      title: successTitle,
      color: "success",
      icon: "material-symbols:check-rounded",
    });
  }

  function error(message: string) {
    if (toastRef) toast.remove(toastRef.id);

    toast.add({
      title: "Erreur",
      description: message,
      color: "error",
      icon: "material-symbols:error-outline-rounded",
    });
  }

  async function runBatch<T>(
    items: T[],
    action: (item: T, options?: { silent?: boolean }) => Promise<void>,
    feedback?: {
      loading: string;
      success: string;
      error?: string;
    },
  ) {
    if (items.length === 1 || !feedback) {
      if (items[0] !== undefined) {
        await action(items[0]);
      }
      return;
    }

    start(feedback.loading, items.length);

    for (const item of items) {
      try {
        await action(item, { silent: true });
        progress();
      } catch (e) {
        error(feedback.error ?? "Une erreur est survenue.");
        return;
      }
    }

    success(feedback.success);
  }

  return { runBatch };
}
