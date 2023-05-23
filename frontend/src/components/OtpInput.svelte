<script lang="ts">
  export let OnOtpEnter: Function;
  export let otpLabel: string = "OTP code";

  let otpCode: string = "";
  let isLoading = false;

  async function loadOtpFun() {
    isLoading = false;
    try {
      await OnOtpEnter(otpCode);
    } catch (error) {}
    otpCode = "";
    isLoading = true;
  }
</script>

{#if !isLoading}
  <form on:submit|preventDefault={loadOtpFun}>
    <nav>
      <div class="max field label fill border">
        <input type="text" bind:value={otpCode} />
        <label for="otp">{otpLabel}</label>
      </div>
      <button class="square extra">
        <i>arrow_forward_ios</i>
      </button>
    </nav>
  </form>
{:else}
  <span class="loader medium" />
{/if}
