export function useBatchAction() {
  const toast = useToast();

  async function runBatch<T>(
    items: T[],
    action: (item: T, options?: { silent?: boolean }) => Promise<void>,
    feedback?: {
      loading: string;
      success: string;
      error?: string;
    },
  ) {
    if (!items.length) return;

    if (items.length === 1 || !feedback) {
      await action(items[0]!);
      return;
    }

    let done = 0;

    const toastRef = toast.add({
      title: feedback.loading,
      description: `0 / ${items.length}`,
      icon: "material-symbols:progress-activity",
      duration: 0,
      progress: false,
      close: false,
      color: "neutral",
      type: "foreground",
      ui: { icon: "animate-spin" },
    });

    for (const item of items) {
      try {
        await action(item, { silent: true });

        done++;

        toast.update(toastRef.id, {
          description: `${done} / ${items.length}`,
        });
      } catch (e) {
        toast.update(toastRef.id, {
          title: "Erreur",
          description: feedback.error ?? "Une erreur est survenue.",
          color: "error",
          icon: "material-symbols:error-outline-rounded",
          duration: 5000,
          close: true,
          ui: { icon: "" },
        });

        return;
      }
    }

    toast.update(toastRef.id, {
      title: feedback.success,
      description: "",
      color: "success",
      icon: "material-symbols:check-rounded",
      duration: 4000,
      close: true,
      ui: { icon: "" },
    });
  }

  return { runBatch };
}
