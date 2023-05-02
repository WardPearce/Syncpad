<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link } from "svelte-navigator";

  import { themeStore } from "../stores";

  export let isRegister = false;

  let mode = isRegister ? "Register" : "Login";
  let passwordScreen = true;

  $: theme = get(themeStore);
  themeStore.subscribe((value) => (theme = value));
</script>

<main class="absolute center">
  <article>
    <h4>{mode}</h4>
    {#if passwordScreen}
      {#if !isRegister}
        <a href="/register" use:link class="link"
          >Need a account? Register here.</a
        >
      {:else}
        <a href="/login" use:link class="link"
          >Already have an account? Login.</a
        >
      {/if}

      <form>
        <div class="field label border medium-divider fill">
          <input type="text" />
          <label for="email">Email</label>
        </div>
        <div class="field label border medium-divider fill">
          <input type="password" />
          <label for="password">Password</label>
        </div>
        {#if isRegister}
          <div class="field label border medium-divider fill">
            <input type="password" />
            <label for="password">Repeat Password</label>
          </div>
        {/if}
        <label class="checkbox">
          <input type="checkbox" />
          <span>Remember me</span>
        </label>

        <div class="right-align" style="margin-top: 1em;">
          <button type="submit">
            <i>login</i>
            <span>{mode}</span>
          </button>
        </div>
      </form>
    {:else}
      {#if isRegister}
        <p>
          Due to the importance of our service, we require all accounts to have
          two factor security.
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
    {/if}
  </article>
</main>

<style>
  @media only screen and (max-width: 600px) {
    main {
      width: 98%;
    }
  }
</style>
