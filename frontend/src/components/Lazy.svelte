<script lang="ts">
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import { localSecrets } from "../stores";
  import { navigate, useLocation } from "svelte-navigator";

  export let component: any;
  export let delayMs: number | null = null;
  export let componentProps = null;
  export let requiresAuth = false;

  let loadedComponent: any = null;
  let timeout: number;
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
    return () => clearTimeout(timeout);
  });
</script>

{#if loadedComponent}
  <svelte:component this={loadedComponent} {...props} {...componentProps} />
{:else if showFallback}
  <slot />
{/if}
