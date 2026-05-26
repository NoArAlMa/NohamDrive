<script lang="ts">
definePageMeta({
  middleware: "prod-middleware",
});
</script>

<template>
  <div class="min-h-screen bg-[--color-bg] p-6 space-y-8">
    <!-- Title -->
    <section>
      <h1 class="text-3xl font-bold text-[--color-text]">
        {{ t("uiPanel.title") }}
      </h1>
      <p class="text-muted">{{ t("uiPanel.subtitle") }}</p>
      <UColorModeSwitch />
    </section>

    <!-- Text samples -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">{{ t("uiPanel.texts") }}</h2>
      </template>

      <div class="flex flex-row gap-6">
        <div class="flex flex-col space-y-2">
          <span class="text-primary">Primary</span>
          <span class="text-secondary">Secondary</span>
          <span class="text-success">Success</span>
          <span class="text-info">Info</span>
          <span class="text-warning">Warning</span>
          <span class="text-error">Error</span>
        </div>
        <div class="flex flex-col space-y-2">
          <span class="text-dimmed">Dimmed</span>
          <span class="text-muted">Muted</span>
          <span class="text-toned">Toned</span>
          <span class="text-default">Text</span>
          <span class="text-highlighted">Highlighted</span>
          <span class="text-inverted bg-inverted">Inverted</span>
        </div>
      </div>
    </UCard>

    <!-- Buttons -->
    <UCard class="bg-[#0D1520]">
      <template #header>
        <h2 class="text-xl font-semibold">{{ t("uiPanel.buttons") }}</h2>
      </template>

      <div class="flex flex-wrap gap-4">
        <UButton color="primary">Primary</UButton>
        <UButton color="secondary">Secondary</UButton>
        <UButton color="neutral">Gray</UButton>
        <UButton color="neutral" variant="soft">Gray Soft</UButton>
        <UButton color="error">Error</UButton>
        <UButton color="success">Success</UButton>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">{{ t("uiPanel.border") }}</h2>
      </template>

      <div class="flex flex-wrap gap-4">
        <div class="border border-default">Default</div>
        <div class="border border-muted">Muted</div>
        <div class="border border-accented">Accented</div>
        <div class="border border-inverted">Inverted</div>
      </div>
    </UCard>

    <!-- Inputs -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">{{ t("uiPanel.inputs") }}</h2>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UInput :placeholder="t('uiPanel.inputStandard')" />
        <UInput :placeholder="t('uiPanel.disabled')" disabled />
        <USelect
          :options="['Option A', 'Option B', 'Option C']"
          :placeholder="t('uiPanel.select')"
        />
        <UTextarea :placeholder="t('uiPanel.textarea')" />
      </div>
    </UCard>

    <!-- Surfaces -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        class="rounded-xl border border-[--color-border] bg-[--color-surface] p-4 shadow-sm"
      >
        <p class="font-medium text-primary">{{ t("uiPanel.surfaceDefault") }}</p>
        <p class="text-sm text-muted">{{ t("uiPanel.surfaceDefaultDesc") }}</p>
      </div>

      <div class="rounded-xl bg-primary p-4 shadow-sm">
        <p class="font-medium">{{ t("uiPanel.surfacePrimary") }}</p>
        <p class="text-sm opacity-90">{{ t("uiPanel.surfacePrimaryDesc") }}</p>
      </div>

      <div class="rounded-xl bg-elevated p-4 shadow-sm">
        <p class="font-medium">{{ t("uiPanel.surfaceLight") }}</p>
        <p class="text-sm">{{ t("uiPanel.surfaceLightDesc") }}</p>
      </div>
    </section>

    <!-- States -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">{{ t("uiPanel.states") }}</h2>
      </template>

      <div class="space-y-3">
        <UAlert color="primary" :title="t('uiPanel.infoTitle')">
          {{ t("uiPanel.infoMessage") }}
        </UAlert>
        <UAlert color="success" :title="t('uiPanel.successTitle')">
          {{ t("uiPanel.successMessage") }}
        </UAlert>
        <UAlert color="warning" :title="t('uiPanel.warningTitle')">
          {{ t("uiPanel.warningMessage") }}
        </UAlert>
        <UAlert color="error" :title="t('uiPanel.errorTitle')">
          {{ t("uiPanel.errorMessage") }}
        </UAlert>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
// Panel de test visuel — aucune logique requise
const { t } = useI18n();
</script>
