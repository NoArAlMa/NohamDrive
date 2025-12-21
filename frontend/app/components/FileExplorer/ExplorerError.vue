<script setup lang="ts">
defineProps<{
  ErrorStatus: number | undefined;
  message: string;
}>();

const { retryFetching } = useFileTree();
</script>

<template>
  <div class="flex items-center justify-center">
    <UEmpty
      class="min-w-[400px]"
      variant="soft"
      icon="material-symbols:error-outline-rounded"
      :description="message"
      :actions="
        ErrorStatus === 500
          ? [
              {
                icon: 'material-symbols:sync-rounded',
                label: 'Refresh',
                color: 'neutral',
                variant: 'subtle',
                size: 'md',
                loadingAuto: true,
                onClick: retryFetching,
              },
            ]
          : []
      "
      size="xl"
    >
      <template #title>
        <h1 :class="ErrorStatus === 500 ? 'text-error' : 'text-warning'">
          Erreur {{ ErrorStatus }}
        </h1>
      </template>
    </UEmpty>
  </div>
</template>
