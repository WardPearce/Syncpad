<script lang="ts">
  import { scale } from "svelte/transition";

  export let duration = 300;
</script>

<div class="route-wrapper" in:scale={{ duration }} out:scale={{ duration }}>
  <slot />
</div>

<style>
  .route-wrapper {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }
</style>
