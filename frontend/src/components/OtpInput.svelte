<script lang="ts">
  export let onOtpEnter: Function;
  export let otpLabel: string = "OTP code";

  let otpCode: string = "";
  let isLoading = false;

  async function loadOtpFunc() {
    isLoading = true;
    try {
      await onOtpEnter(otpCode);
    } catch (error) {}
    otpCode = "";
    isLoading = false;
  }
</script>

{#if !isLoading}
  <form on:submit|preventDefault={loadOtpFunc}>
    <nav>
      <div class="max field label fill border">
        <input type="text" bind:value={otpCode} />
        <label for="otp">{otpLabel}</label>
      </div>
      <button class="square round extra">
        <i>arrow_forward_ios</i>
      </button>
    </nav>
  </form>
{:else}
  <span class="loader medium" />
{/if}
