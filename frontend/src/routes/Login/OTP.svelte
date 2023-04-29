<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { themeStore } from "../../stores";
  import { get } from "svelte/store";

  export let isRegister = false;

  $: theme = get(themeStore);
  themeStore.subscribe((value) => (theme = value));
</script>

{#if isRegister}
  <p>
    Due to the importance of our service, we require all accounts to have two
    factor security.
  </p>
  <p>Please scan the following QR code to continue.</p>
  <div class="center-align">
    <QrCode
      value="https://github.com/"
      background={theme["--surface"]}
      color={theme["--primary"]}
    />
  </div>
{:else}
  <p>Please enter your OTP code to contiue.</p>
{/if}

<nav>
  <div class="max field label fill border">
    <input type="text" />
    <label for="otp">8 digit OTP code</label>
  </div>
  <button class="square extra">
    <i>arrow_forward_ios</i>
  </button>
</nav>
