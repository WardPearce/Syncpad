<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link, navigate, useLocation } from "svelte-navigator";
  import { tooltip } from "@svelte-plugins/tooltips";

  import { advanceModeStore, localSecrets, themeStore } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import apiClient from "../lib/apiClient";
  import { type UserJtiModel } from "../lib/client";
  import { onMount } from "svelte";
  import OtpInput from "../components/OtpInput.svelte";

  export let isRegister = false;

  $: mode = isRegister ? "Register" : "Login";
  let otpSetupRequired = false;
  let passwordScreen = true;
  let errorMsg = "";
  let advanceModeMsg = "";
  let isLoading = false;

  let currentLocation = get(useLocation());
  let redirectPath: string | undefined = currentLocation.state
    ? currentLocation.state.redirect
    : undefined;

  let email = "";
  let rawPassword = "";
  let captchaToken = "";
  let deviceSessionLogs = true;

  let loggedInUser: UserJtiModel;

  let theme;
  themeStore.subscribe((value) => (theme = value));

  let advanceMode;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  onMount(() => {
    if (get(localSecrets) !== undefined) {
      navigate("/dashboard", { replace: true });
    }
  });

  async function OnOtpEnter(otpCode: string) {
    isLoading = true;
    errorMsg = "";

    advanceModeMsg = "Validating OTP code";

    if (otpSetupRequired) {
      try {
        await apiClient.account.controllersAccountOtpSetupOtpSetup(otpCode);
      } catch (error) {
        errorMsg = error.body.detail;
        isLoading = false;
        return;
      }
    } else {
      try {
        await attemptAuthorization(otpCode);
      } catch (error) {
        errorMsg = error;
        passwordScreen = true;
        rawPassword = "";
        isLoading = false;
        return;
      }
    }

    navigate(redirectPath !== undefined ? redirectPath : "/dashboard", {
      replace: true,
    });

    isLoading = false;
  }
</script>

<main class="absolute center">
  <article>
    {#if isLoading}
      <div style="display: flex; flex-direction: column;align-items: center;">
        <h4>Loading</h4>
        <p>Please wait, this may take a moment.</p>
        <span style="margin: 1em 0;" class="loader large" />

        {#if advanceMode}
          <div style="font-style: italic;text-align: center;">
            <p style="font-weight: bold;">Advance comment</p>
            <p>{advanceModeMsg}</p>
          </div>
        {/if}
      </div>
    {:else}
      <h4>{mode}</h4>
      {#if redirectPath !== undefined}
        <p style="margin-bottom: 1em;">
          Authorization required to access that page.
        </p>
      {/if}

      {#if errorMsg}
        <div class="red5">
          <p>{errorMsg}</p>
        </div>
      {/if}

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
        <form on:submit|preventDefault={onLogin} id="login">
          <div class="field label border medium-divider fill">
            <input type="text" bind:value={email} />
            <label for="email">Email</label>
          </div>
          <div class="field label border medium-divider fill">
            <input type="password" bind:value={rawPassword} />
            <label for="password">Password</label>
          </div>

          {#if isRegister}
            <label
              class="checkbox"
              use:tooltip={{
                content:
                  "IP & device processed for session logs on login. Encrypted with your public key. Your IP will be processed with Proxycheck.io",
              }}
            >
              <input type="checkbox" bind:checked={deviceSessionLogs} />
              <span>Device session logs</span>
            </label>
          {/if}

          <Mcaptcha bind:captchaToken />

          <div class="right-align" style="margin-top: 1em;">
            <button type="submit">
              <i>login</i>
              <span>{mode}</span>
            </button>
          </div>
        </form>
      {:else}
        {#if otpSetupRequired}
          <p>
            Due to the importance of our service, we require all accounts to
            have two factor security.
          </p>
          <p>Please scan the following QR code to continue.</p>
          <div
            style="display: flex;flex-direction: column;align-items: center;row-gap: 1em;"
          >
            <QrCode
              value={loggedInUser.user.otp.provisioning_uri}
              background={theme["--surface"]}
              color={theme["--primary"]}
            />
            <button
              on:click={async () => {
                await navigator.clipboard.writeText(
                  loggedInUser.user.otp.secret
                );
              }}
            >
              <i>vpn_key</i>
              <span>Copy secret</span>
            </button>
          </div>
        {/if}

        <OtpInput {OnOtpEnter} />
      {/if}
    {/if}
  </article>
</main>

<style>
  @media only screen and (max-width: 600px) {
    main {
      width: 98%;
    }
  }

  .red5 {
    padding: 0.5em 1em;
    margin: 1em 0;
  }
</style>
