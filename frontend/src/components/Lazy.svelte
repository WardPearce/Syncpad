<script lang="ts">
  import { onMount } from "svelte";

  export let component: any;
  export let delayMs: number | null = null;
  export let componentProps = null;

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
