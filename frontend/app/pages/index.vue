<script lang="ts" setup>
import type { ButtonProps, PageFeatureProps } from "@nuxt/ui";

useHead({
  title: "Welcome - NohamDrive",
  meta: [
    {
      name: "NohamDrive | Welcome Page",
      content: "Discover the open-source alternative of Onedrive",
    },
  ],
});

useSeoMeta({
  description: "Discover the open-source alternative of Onedrive",
  ogTitle: "Welcome - NohamDrive",
  ogDescription: "Discover the open-source alternative of Onedrive",
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: "Welcome - NohamDrive",
  twitterDescription: "Discover the open-source alternative of Onedrive",
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});

definePageMeta({
  layout: "welcome",
  middleware: "app-middleware",
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
    icon: "terminal:echo-icon",
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
      name: "Eric Z.",
      description: "CEO chez Reconquête",
      avatar: {
        src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJR0X94RYBQIXn1m_-ZCiwPpiZZ8OQGhua-g&s",
        alt: "Eric Z.",
      },
    },
    quote:
      "Eh ben voyons ! NohamDrive a révolutionné notre gestion des arabes à renvoyer dans leurs pays. Le terminal intégré est un game-changer : enfin une alternative open-source à OneDrive qui répond à nos besoins techniques !",
    star: 4,
  },
  {
    user: {
      name: "Adolf H.",
      description: "Développeur full-stack freelance",
      avatar: {
        src: "https://ichef.bbci.co.uk/ace/ws/640/cpsprodpb/DD74/production/_126329665_fea34d36-80f3-4987-b7e2-509a67afecdd.jpg.webp",
        alt: "Adolf H.",
      },
    },
    quote:
      "J’ai été rejeté des Beaux-arts étant plus jeune. L’intégration avec Minio et le terminal Linux-like m’ont convaincu : c’est l’outil qu’il me manquait pour mes projets.",
    star: 3,
  },
  {
    user: {
      name: "Le minotaure",
      description: "Responsable des Furry",
      avatar: {
        src: "https://m.media-amazon.com/images/S/amzn-author-media-prod/o7o0ubb64o29ardj4phsr3sfg3._SY450_CR0%2C0%2C450%2C450_.jpg",
        alt: "Le minotaure",
      },
    },
    quote:
      "C'EST LE TRAIN DE LA HYYYYYPE !! Johan adore cette application ! Cela nous permet de nous organiser pour faire les vidéos dégustation",
    star: 4,
  },
  {
    user: {
      name: "Walter W.",
      description: "Professeur de chimie",
      avatar: {
        src: "https://upload.wikimedia.org/wikipedia/en/0/03/Walter_White_S5B.png",
        alt: "Walter W.",
      },
    },
    quote:
      "Depuis que j'utilise NohamDrive, je suis le danger. Grâce à NohamDrive, Skyler gère mieux le blanchiment d'argent et surtout elle ouvre moins sa gueule",
    star: 5,
  },
  {
    user: {
      name: "Hugo H.",
      description: "CEO exceptionnel de Roblox",
      avatar: {
        src: "https://media.routard.com/image/41/1/pt54785.1264411.jpg",
        alt: "Hugo H.",
      },
    },
    quote: "Miaou",
    star: 5,
  },

  {
    user: {
      name: "Elizabeth II",
      description: "Sysadmin au paradis",
      avatar: {
        src: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Elizabeth_II_in_Berlin_2015_%28cropped%29.JPG/250px-Elizabeth_II_in_Berlin_2015_%28cropped%29.JPG",
        alt: "Elizabeth II",
      },
    },
    quote:
      "L’intégration avec notre infrastructure existante (PostgreSQL + Docker) a été un jeu d’enfant. Les performances sont au rendez-vous, même avec des fichiers volumineux.",
    star: 4,
  },
  {
    user: {
      name: "Cémoi lebaigé.",
      description: "Vendeur de Kebab",
      avatar: {
        src: "https://i.pinimg.com/736x/41/18/04/411804a00535829a3e910e7ad2a1bf45.jpg",
        alt: "Cémoi lebaigé.",
      },
    },
    quote:
      "Ahah ne trouvez vous pas ça magnifique, mon cher ! Cette application est vraiment très belle et je l'aime bien. Un gain de temps énorme !",
    star: 4,
  },
  {
    user: {
      name: "Christian R.",
      description: "Joueur de sucker",
      avatar: {
        src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLp39lxGZQV78_C3WuLpD7K9b1giOmPGtZCA&s",
        alt: "Christian R.",
      },
    },
    quote: "SIUUU… mes backups sont sécurisés.",
    star: 3,
  },
  {
    user: {
      name: "Jeffrey E.",
      description: "Design Lead chez Nickelodeon",
      avatar: {
        src: "https://media.lesechos.com/api/v1/images/view/5d5b7881d286c205b067c1e4/1280x720/0601738550212-web-tete.jpg",
        alt: "Jeffrey E.",
      },
    },
    quote:
      "Enfin un outil qui allie simplicité et puissance ! Mes équipes adorent explorer les enfants... euh les fichiers, et moi, je dors sur mes deux oreilles grâce au chiffrement intégré ; ).",
    star: 3,
  },

  {
    user: {
      name: "Monsieur Bride'o'neaut",
      description: "CEO des graphes",
      avatar: {
        src: "https://pierrelacroix.com/wp-content/uploads/2009/07/coeur-de-dieu.jpg",
        alt: "Monsieur Bride'o'neaut",
      },
    },
    quote:
      "Franchement j'ai bien aimé, c'est pas trop difficile à installer ! C'est mon mac qui m'a le plus ralenti. Je sais pas vraiment comment ça fonctionne mais j'imagine que c'est bien",
    star: 3,
  },
  {
    user: {
      name: "Donald D.",
      description: "CEO des Etats Unis",
      avatar: {
        src: "https://www.trumplibrary.gov/sites/default/files/styles/large/public/2021-01/President-Trump-Official-Portrait.jpg?itok=eReCLE7X",
        alt: "Donald D.",
      },
    },
    quote:
      "J'adore NohamDrive ! Et j'adore la France, Macron est un nice guy. Make NohamDrive great again !!",
    star: 4,
  },
  {
    user: {
      name: "Jay Lense",
      description: "Professeur en informatique",
      avatar: {
        src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBcmfL2liSkvMLJ7KJE925MM7kSlBjx6sPRg&s",
        alt: "Jay Lance",
      },
    },
    quote:
      "Windows c'est de la merde, tout le monde le sait ! C'est pour ça que j'ai décidé d'utiliser la meilleure alternative à Onedrive (cette merde) : NohamDrive ! J'apprécie cette app presque autant que Linux",
    star: 5,
  },
]);

const PageTitle = "Stock, share & collaborate freely";
const PageDesc = ref(
  "NohamDrive est une alternative open-source à OneDrive, conçue pour les équipes. Explorez, partagez et gérez vos fichiers directement depuis un terminal intégré et une interface intuitive, en toute sécurité.",
);
</script>

<template>
  <section class="flex flex-col scroll-smooth">
    <UPageSection
      :features="pageSection"
      :title="PageTitle"
      :description="PageDesc"
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
      class="min-h-[80vh] w-full flex flex-col rounded-md md:flex-row items-center justify-center gap-12 px-4 sm:px-8 py-12 bg-gray-800"
    >
      <div class="flex-1 max-w-md text-center md:text-left">
        <h1
          class="text-5xl sm:text-5xl font-bold flex items-center justify-center md:justify-start gap-3 mb-6"
        >
          Découvrez Echo
          <UIcon name="terminal:echo-icon" class="text-primary" dynamic />
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
          icon="material-symbols:arrow-forward-rounded"
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
    <div id="testimonials" class="py-16 px-4 sm:py-20 sm:px-6 lg:py-24 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <h2
          class="text-3xl sm:text-4xl md:text-5xl font-bold text-center mb-12 md:mb-16"
        >
          Ils nous font confiance
        </h2>

        <UPageColumns>
          <UPageCard
            v-for="(testimonial, index) in testimonials"
            :key="index"
            variant="subtle"
            :description="testimonial.quote"
            :ui="{
              description:
                'before:content-[open-quote] after:content-[close-quote]',
            }"
          >
            <template #header>
              <div class="w-full flex flex-row justify-between items-center">
                <UIcon
                  v-for="i in 5"
                  :key="i"
                  :name="
                    i <= testimonial.star
                      ? 'material-symbols:star-rate-rounded'
                      : 'material-symbols:star-rate-outline-rounded'
                  "
                  class="size-5"
                  :class="
                    i <= testimonial.star
                      ? 'text-amber-400'
                      : 'text-neutral-500'
                  "
                />
              </div>
            </template>
            <template #footer>
              <UUser v-bind="testimonial.user" size="xl" />
            </template>
          </UPageCard>
        </UPageColumns>
      </div>
    </div>
  </section>
</template>
