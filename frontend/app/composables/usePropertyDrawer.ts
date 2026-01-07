const drawerOpen = ref(false);
const currentItemProperties = ref<FileMetadata | null>(null);

export function usePropertyDrawer() {
  const openDrawerWithProperties = (properties: FileMetadata) => {
    currentItemProperties.value = properties;
    drawerOpen.value = true;
  };

  const closeDrawer = () => {
    drawerOpen.value = false;
    currentItemProperties.value = null;
  };

  return {
    drawerOpen,
    currentItemProperties,
    openDrawerWithProperties,
    closeDrawer,
  };
}
