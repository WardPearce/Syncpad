<script lang="ts">
  import Password from "./Password.svelte";
  import Otp from "./OTP.svelte";

  export let isRegister = false;

  let mode = isRegister ? "Register" : "Login";
  let passwordScreen = true;
</script>

<main class="absolute center">
  <h4>{mode}</h4>

  <article>
    {#if passwordScreen}
      <Password {isRegister} {mode} />
    {:else}
      <Otp {isRegister} />
    {/if}
  </article>
</main>

<style>
</style>
