<script lang="ts">
  import Widget from "@mcaptcha/svelte-glue/src/lib/Widget.svelte";
  const mcaptchaConfig = {
    widgetLink: new URL(import.meta.env.VITE_MCAPTCHA_WIDGET),
  };
</script>

{#if import.meta.env.VITE_MCAPTCHA_WIDGET}
  <div>
    <Widget config={mcaptchaConfig} />
  </div>
{/if}

<style>
  div {
    background-color: #f4eff4;
    width: 100%;
    display: flex;
    margin-top: 1em;
  }
</style>
