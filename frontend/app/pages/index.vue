<script lang="ts" setup>
import type { ButtonProps, PageFeatureProps } from "@nuxt/ui";

definePageMeta({
  layout: "welcome",
});

const features = [
  {
    title: "Explorateur de fichiers avancé",
    description:
      "Naviguez dans vos fichiers comme sur votre ordinateur, avec un terminal intégré pour une gestion rapide et précise.",
    icon: "material-symbols:folder",
  },
  {
    title: "Partage sécurisé et collaboratif",
    description:
      "Partagez des fichiers ou dossiers en un clic, avec des permissions personnalisables et un historique des modifications.",
    icon: "material-symbols:share",
  },
  {
    title: "100% Open-Source",
    description:
      "Un code transparent, modifiable et auditable par tous. Rejoignez notre communauté pour contribuer ou adapter NohamDrive à vos besoins.",
    icon: "material-symbols:code-rounded",
  },
];

const pageSection = ref<PageFeatureProps[]>([
  {
    title: "Terminal Echo",
    description:
      "Gérez vos fichiers en ligne de commande directement dans le cloud, comme sur un système Linux.",
    icon: "mdi:star-four-points-outline",
  },
  {
    title: "Collaboration en temps réel",
    description:
      "Partagez, commentez et éditez des fichiers à plusieurs, avec des notifications instantanées et un historique des changements.",
    icon: "material-symbols:group-outline-rounded",
  },
  {
    title: "Sécurité et confidentialité",
    description:
      "Vos données sont chiffrées et protégées. Contrôlez les accès et les permissions pour chaque membre de votre équipe.",
    icon: "material-symbols:lock-outline",
  },
]);

const links = ref<ButtonProps[]>([
  {
    label: "Get started",
    to: "/auth",
    icon: "material-symbols:play-arrow-outline-rounded",
  },
  {
    label: "Learn more",
    to: "#features",
    color: "neutral",
    variant: "subtle",
    trailingIcon: "material-symbols:arrow-forward-rounded",
  },
]);

const testimonials = ref([
  {
    user: {
      name: "Thomas L.",
      description: "CTO chez DevFlow",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/32.jpg",
        alt: "Thomas L.",
      },
    },
    quote:
      "NohamDrive a révolutionné notre gestion de fichiers en équipe. Le terminal intégré est un game-changer : enfin une alternative open-source à OneDrive qui répond à nos besoins techniques !",
  },
  {
    user: {
      name: "Clara M.",
      description: "Cheffe de projet chez OpenTech",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/44.jpg",
        alt: "Clara M.",
      },
    },
    quote:
      "Passé de OneDrive à NohamDrive en une semaine, et nos équipes ne veulent plus revenir en arrière. La collaboration en temps réel et la transparence du code sont des atouts majeurs.",
  },
  {
    user: {
      name: "Lucas D.",
      description: "Développeur full-stack freelance",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/65.jpg",
        alt: "Lucas D.",
      },
    },
    quote:
      "J’ai déployé NohamDrive sur mon VPS en moins de 30 minutes. L’intégration avec Minio et le terminal Linux-like m’ont convaincu : c’est l’outil qu’il me manquait pour mes projets clients.",
  },
  {
    user: {
      name: "Amélie R.",
      description: "Responsable IT chez GreenStart",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/68.jpg",
        alt: "Amélie R.",
      },
    },
    quote:
      "Nos données sensibles sont enfin hébergées en interne, avec un contrôle total. L’interface est intuitive, et le support communautaire est réactif. Un sans-faute !",
  },
  {
    user: {
      name: "Julien P.",
      description: "Co-fondateur de CodeHub",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/75.jpg",
        alt: "Julien P.",
      },
    },
    quote:
      "Le partage sécurisé et l’historique des modifications ont réduit nos erreurs de 40%. NohamDrive est devenu notre outil de référence pour la gestion de documents techniques.",
  },
  {
    user: {
      name: "Sophie T.",
      description: "Design Lead chez UX Studio",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/28.jpg",
        alt: "Sophie T.",
      },
    },
    quote:
      "Enfin un outil qui allie simplicité et puissance ! Mes équipes adorent l’explorateur de fichiers, et moi, je dors sur mes deux oreilles grâce au chiffrement intégré.",
  },
  {
    user: {
      name: "Antoine B.",
      description: "Sysadmin chez CloudInnov",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/82.jpg",
        alt: "Antoine B.",
      },
    },
    quote:
      "L’intégration avec notre infrastructure existante (PostgreSQL + Docker) a été un jeu d’enfant. Les performances sont au rendez-vous, même avec des fichiers volumineux.",
  },
  {
    user: {
      name: "Camille L.",
      description: "Product Manager chez StartUp Factory",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/36.jpg",
        alt: "Camille L.",
      },
    },
    quote:
      "NohamDrive a accéléré nos workflows de 30%. Le terminal intégré permet à nos devs de gérer les fichiers sans quitter leur environnement préféré. Un gain de temps énorme !",
  },
  {
    user: {
      name: "Marc S.",
      description: "Professeur en informatique",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/41.jpg",
        alt: "Marc S.",
      },
    },
    quote:
      "J’utilise NohamDrive pour enseigner la gestion de fichiers à mes étudiants. L’outil est pédagogique, et le code open-source leur permet de comprendre ‘sous le capot’. Bravo !",
  },
  {
    user: {
      name: "Élodie F.",
      description: "Freelance en cybersécurité",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/55.jpg",
        alt: "Élodie F.",
      },
    },
    quote:
      "La sécurité est au cœur de NohamDrive : permissions granulaires, chiffrement, et audits complets. Je le recommande à tous mes clients soucieux de protéger leurs données.",
  },
  {
    user: {
      name: "Nicolas K.",
      description: "CEO de TechForGood",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/12.jpg",
        alt: "Nicolas K.",
      },
    },
    quote:
      "Nous avons migré 5 To de données vers NohamDrive sans aucun temps d’arrêt. L’équipe a été bluffée par la stabilité et la réactivité du support.",
  },
  {
    user: {
      name: "Laura V.",
      description: "Cheffe de produit chez DataDrive",
      avatar: {
        src: "https://randomuser.me/api/portraits/women/79.jpg",
        alt: "Laura V.",
      },
    },
    quote:
      "L’outil parfait pour les équipes techniques : léger, rapide, et sans dépendance à des solutions propriétaires. Nos coûts d’hébergement ont chuté de 50% !",
  },
  {
    user: {
      name: "Pierre M.",
      description: "Développeur backend",
      avatar: {
        src: "https://randomuser.me/api/portraits/men/9.jpg",
        alt: "Pierre M.",
      },
    },
    quote:
      "J’ai contribué au code de NohamDrive, et c’est un plaisir de voir un projet open-source aussi bien structuré. La documentation est claire, et la communauté est accueillante.",
  },
]);

const PageTitle = "Stock, share & collaborate freely";
</script>

<template>
  <section class="flex flex-col">
    <UPageSection
      :features="pageSection"
      :title="PageTitle"
      description="NohamDrive est une alternative open-source à OneDrive, conçue pour les équipes. Explorez, partagez et gérez vos fichiers directement depuis un terminal intégré et une interface intuitive, en toute sécurité."
      :links="links"
      class="w-full h-[90vh] mb-10"
    />

    <div id="features" class="py-16 px-4 sm:py-20 sm:px-6 lg:py-24 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <h2
          class="text-3xl sm:text-4xl md:text-5xl font-bold text-center mb-12 md:mb-16"
        >
          Tout ce dont vous avez besoin<br class="hidden sm:block" />
          pour gérer vos fichiers en équipe
        </h2>
        <UPageGrid
          class="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8"
        >
          <UPageCard
            v-for="(card, index) in features"
            :key="index"
            v-bind="card"
            :ui="{
              title: 'mb-3',
            }"
            class="h-full hover:shadow-lg transition-all duration-300 hover:transform hover:-translate-y-1"
          />
        </UPageGrid>
      </div>
    </div>

    <div
      id="echo"
      class="min-h-[70vh] w-full flex flex-col rounded-md md:flex-row items-center justify-center gap-12 px-4 sm:px-8 py-12 bg-gray-800"
    >
      <div class="flex-1 max-w-md text-center md:text-left">
        <h1
          class="text-5xl sm:text-5xl font-bold flex items-center justify-center md:justify-start gap-3 mb-6"
        >
          Découvrez Echo
          <UIcon
            name="mdi:star-four-points-outline"
            class="text-primary"
            dynamic
          />
        </h1>
        <p class="text-lg sm:text-x mb-8 max-w-lg">
          Une façon révolutionnaire de naviguer entre vos dossiers et fichiers,
          <span class="font-semibold">intuitive, rapide et puissante.</span>
        </p>
        <UButton
          label="En savoir plus"
          color="primary"
          variant="solid"
          size="lg"
          class="mx-auto md:mx-0"
          icon="i-heroicons-arrow-right"
        />
      </div>

      <div
        class="flex-1 max-w-none md:max-w-2xl lg:max-w-3xl xl:max-w-4xl relative"
      >
        <div class="relative rounded-xl overflow-hidden shadow-2xl">
          <video
            autoplay
            loop
            muted
            playsinline
            class="w-full h-auto rounded-xl"
            style="max-width: 100%; height: auto; aspect-ratio: 16/9"
            src="https://www.pexels.com/fr-fr/download/video/2887463/"
          ></video>
        </div>
      </div>
    </div>
  </section>
</template>

<style>
html {
  scroll-behavior: smooth;
}
</style>
