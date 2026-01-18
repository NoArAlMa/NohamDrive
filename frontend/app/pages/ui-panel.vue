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
        Color & UI Test Panel
      </h1>
      <p class="text-muted">
        Panneau de test pour la palette (textes, surfaces, boutons, inputs)
      </p>
      <UColorModeSwitch />
    </section>

    <!-- Text samples -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Textes</h2>
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
        <h2 class="text-xl font-semibold">Boutons</h2>
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
        <h2 class="text-xl font-semibold">Border</h2>
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
        <h2 class="text-xl font-semibold">Inputs</h2>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UInput placeholder="Input standard" />
        <UInput placeholder="Disabled" disabled />
        <USelect
          :options="['Option A', 'Option B', 'Option C']"
          placeholder="Select"
        />
        <UTextarea placeholder="Textarea" />
      </div>
    </UCard>

    <!-- Surfaces -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm"
      >
        <p class="font-medium text-primary">Surface Default</p>
        <p class="text-sm text-muted">Surface principale</p>
      </div>

      <div class="rounded-xl bg-primary p-4 shadow-sm">
        <p class="font-medium">Surface Primary</p>
        <p class="text-sm opacity-90">Accent / highlight</p>
      </div>

      <div class="rounded-xl bg-elevated p-4 shadow-sm">
        <p class="font-medium">Surface Light</p>
        <p class="text-sm">Background léger</p>
      </div>
    </section>

    <!-- States -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">États</h2>
      </template>

      <div class="space-y-3">
        <UAlert color="primary" title="Info">Message d'information</UAlert>
        <UAlert color="success" title="Succès">Action réussie</UAlert>
        <UAlert color="warning" title="Warning">Attention</UAlert>
        <UAlert color="error" title="Erreur">Une erreur est survenue</UAlert>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
// Panel de test visuel — aucune logique requise
</script>
