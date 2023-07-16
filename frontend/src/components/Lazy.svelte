<script lang="ts">
  import { onMount } from "svelte";
  import { navigate, useLocation } from "svelte-navigator";
  import { get } from "svelte/store";
  import { getCurrentThemePrimary } from "../lib/theme";
  import { localSecrets } from "../stores";

  export let component: any;
  export let delayMs: number | null = null;
  export let componentProps: Record<string, any> | null = null;
  export let requiresAuth = false;

  let loadedComponent: any = null;
  let timeout: NodeJS.Timeout;
  let showFallback = !delayMs;

  let props: Record<any, any>;
  $: {
    // eslint-disable-next-line no-shadow
    const { component, requiresAuth, componentProps, delayMs, ...restProps } =
      $$props;
    props = restProps;
  }

  if (requiresAuth) {
    if (get(localSecrets) === undefined) {
      navigate("/login", {
        replace: true,
        state: { redirect: get(useLocation()).pathname },
      });
    }
  }

  onMount(async () => {
    if (delayMs) {
      timeout = setTimeout(() => {
        showFallback = true;
      }, delayMs);
    }
    component().then((module) => {
      loadedComponent = module.default;
    });

    // Set theme on each page load.
    await ui("theme", getCurrentThemePrimary());

    return () => clearTimeout(timeout);
  });
</script>

{#if loadedComponent}
  <svelte:component this={loadedComponent} {...props} {...componentProps} />
{:else if showFallback}
  <slot />
{/if}
