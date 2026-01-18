<script setup lang="ts">
const props = defineProps<{
  ErrorStatus: number | undefined;
  message: string;
  onRetry: () => void;
}>();


</script>

<template>
  <div class="flex items-center justify-center">
    <UEmpty
      class="min-w-100"
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
                onClick: props.onRetry,
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
