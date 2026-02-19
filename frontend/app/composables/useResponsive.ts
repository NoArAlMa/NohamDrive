import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";

export function useResponsive() {
  const breakpoints = useBreakpoints(breakpointsTailwind);

  const isMobile = breakpoints.smaller("md");
  const isDesktop = breakpoints.greaterOrEqual("lg");

  return { isMobile, isDesktop };
}
