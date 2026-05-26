<script lang="ts" setup>
import type { ButtonProps, PageFeatureProps } from "@nuxt/ui";

const { $t } = useI18n();

useHead(() => ({
  title: String($t("seo.welcomeTitle")),
  htmlAttrs: {
    class: "scroll-smooth",
  },
  meta: [
    {
      name: "NohamDrive | Welcome Page",
      content: String($t("seo.welcomeDescription")),
    },
  ],
}));

useSeoMeta({
  description: String($t("seo.welcomeDescription")),
  ogTitle: String($t("seo.welcomeTitle")),
  ogDescription: String($t("seo.welcomeDescription")),
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: String($t("seo.welcomeTitle")),
  twitterDescription: String($t("seo.welcomeDescription")),
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});
definePageMeta({
  layout: "welcome",
  middleware: "app-middleware",
});

const { isMobile } = useResponsive();

const features = computed(() => [
  {
    title: String($t("welcome.cards.advancedExplorer.title")),
    description: String($t("welcome.cards.advancedExplorer.description")),
    icon: "material-symbols:folder",
  },
  {
    title: String($t("welcome.cards.secureSharing.title")),
    description: String($t("welcome.cards.secureSharing.description")),
    icon: "material-symbols:share",
  },
  {
    title: String($t("welcome.cards.openSource.title")),
    description: String($t("welcome.cards.openSource.description")),
    icon: "material-symbols:code-rounded",
  },
]);

const pageSection: PageFeatureProps[] = [
  {
    title: $t("welcome.sections.terminalEcho.title") as string,
    description: $t("welcome.sections.terminalEcho.description") as string,
    icon: "terminal:echo-icon",
  },
  {
    title: $t("welcome.sections.realtimeCollab.title") as string,
    description: $t("welcome.sections.realtimeCollab.description") as string,
    icon: "material-symbols:group-outline-rounded",
  },
  {
    title: $t("welcome.sections.security.title") as string,
    description: $t("welcome.sections.security.description") as string,
    icon: "material-symbols:lock-outline",
  },
];

const links = computed<ButtonProps[]>(() => [
  {
    label: $t("common.getStarted") as string,
    to: "/auth",
    icon: "material-symbols:play-arrow-outline-rounded",
  },
  {
    label: $t("common.learnMore") as string,
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
    quote: $t("welcome.testimonials.t1"),
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
    quote: $t("welcome.testimonials.t2"),
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
    quote: $t("welcome.testimonials.t3"),
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
    quote: $t("welcome.testimonials.t4"),
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
    quote: $t("welcome.testimonials.t5"),
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
    quote: $t("welcome.testimonials.t6"),
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
    quote: $t("welcome.testimonials.t7"),
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
    quote: $t("welcome.testimonials.t8"),
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
    quote: $t("welcome.testimonials.t9"),
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
    quote: $t("welcome.testimonials.t10"),
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
    quote: $t("welcome.testimonials.t11"),
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
    quote: $t("welcome.testimonials.t12"),
    star: 5,
  },
]);

const PageTitle = computed(() => String($t("welcome.heroTitle")));
const PageDesc = computed(() => String($t("welcome.heroDesc")));
</script>

<template>
  <section class="flex flex-col">
    <div class="min-h-screen">
      <UPageSection
        :features="pageSection"
        :title="PageTitle"
        :description="PageDesc"
        :links="links"
        class="mb-10"
      />

      <div id="features" class="py-16 px-4 sm:py-20 sm:px-6 lg:py-24 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <h2
            v-if="isMobile"
            class="text-3xl sm:text-4xl md:text-5xl font-bold text-center mb-12 md:mb-16"
          >
            {{ $t("welcome.featuresHeadingMobile") }}
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
    </div>
    <div
      id="echo"
      class="min-h-[80vh] w-full flex flex-col rounded-md md:flex-row items-center justify-center gap-12 px-4 sm:px-8 py-12 bg-gray-200 dark:bg-gray-800"
    >
      <div class="flex-1 max-w-md text-center md:text-left">
        <h1
          class="text-5xl sm:text-5xl font-bold flex items-center justify-center md:justify-start gap-3 mb-6"
        >
          {{ $t("welcome.echoHeading") }}
          <UIcon name="terminal:echo-icon" class="text-primary" dynamic />
        </h1>
        <p class="text-lg sm:text-x mb-8 max-w-lg">
          {{ $t("welcome.echoLead") }}
          <span class="font-semibold">{{ $t("welcome.echoLeadStrong") }}</span>
        </p>
        <UButton
          :label="String($t('common.learnMore'))"
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
          {{ $t("welcome.trustHeading") }}
        </h2>

        <UPageColumns>
          <UPageCard
            v-for="(testimonial, index) in testimonials"
            :key="index"
            variant="subtle"
            :description="String(testimonial.quote)"
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
                      : 'text-neutral-600'
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
