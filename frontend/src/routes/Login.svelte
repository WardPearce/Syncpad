<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link, navigate, useLocation } from "svelte-navigator";
  import { tooltip } from "@svelte-plugins/tooltips";

  import { advanceModeStore, localSecrets, themeStore } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import { type UserModel } from "../lib/client";
  import { onMount } from "svelte";
  import OtpInput from "../components/OtpInput.svelte";
  import account, { OtpRequiredError } from "../lib/account";
  import apiClient from "../lib/apiClient";

  export let isRegister = false;

  $: mode = isRegister ? "Register" : "Login";

  let otpSetupRequired = false;
  let passwordScreen = true;
  let isLoading = false;

  let errorMsg = "";
  let advanceModeMsg = "";

  let currentLocation = get(useLocation());
  let redirectPath: string | undefined = currentLocation.state
    ? currentLocation.state.redirect
    : undefined;

  let email = "";
  let password = "";
  let captchaToken = "";
  let ipConsent = false;

  let loggedInUser: UserModel;

  const passwordCache = {
    pastPassword: {
      raw: "",
      derived: new Uint8Array([]),
    },
  };

  let theme;
  themeStore.subscribe((value) => (theme = value));

  let advanceMode;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  onMount(() => {
    if (get(localSecrets) !== undefined) {
      navigate("/dashboard", { replace: true });
    }
  });

  async function onAuth() {
    isLoading = true;
    errorMsg = "";

    try {
      if (!isRegister) {
        for await (const result of account.login(
          email,
          password,
          captchaToken,
          undefined,
          passwordCache
        )) {
          if (typeof result === "string") {
            advanceModeMsg = result;
          } else {
            loggedInUser = result;
            if (!loggedInUser.otp.completed) {
              passwordScreen = false;
              otpSetupRequired = true;
            }
          }
        }
      } else {
        for await (const result of account.register(
          email,
          password,
          captchaToken,
          ipConsent
        )) {
          advanceModeMsg = result;
        }

        otpSetupRequired = true;
      }

      password = "";
      isRegister = false;
    } catch (error) {
      if (error instanceof OtpRequiredError) {
        passwordScreen = false;
        otpSetupRequired = false;
      } else {
        passwordScreen = true;
        errorMsg = error.message;
      }
    }

    isLoading = false;
  }

  async function onOtpEnter(otpCode: string) {
    isLoading = true;
    errorMsg = "";

    if (otpSetupRequired) {
      try {
        await apiClient.account.controllersAccountOtpSetupOtpSetup(otpCode);
        navigate(redirectPath ? redirectPath : "/dashboard", {
          replace: true,
        });
      } catch (error) {
        errorMsg = error.body.detail;
      }
    } else {
      try {
        for await (const result of account.login(
          email,
          password,
          captchaToken,
          otpCode,
          passwordCache
        )) {
          if (typeof result === "string") {
            advanceModeMsg = result;
          } else {
            navigate(redirectPath ? redirectPath : "/dashboard", {
              replace: true,
            });
          }
        }
      } catch (error) {
        errorMsg = error.message;
        password = "";
        passwordScreen = true;
      }
    }

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
        <form on:submit|preventDefault={onAuth} id="login">
          <div class="field label border medium-divider fill">
            <input type="text" bind:value={email} />
            <label for="email">Email</label>
          </div>
          <div class="field label border medium-divider fill">
            <input type="password" bind:value={password} />
            <label for="password">Password</label>
          </div>

          {#if isRegister}
            <label
              class="checkbox"
              use:tooltip={{
                content:
                  "Your IP will be processed with Proxycheck.io for session logs on login. Stored encrypted with your public key.",
              }}
            >
              <input type="checkbox" bind:checked={ipConsent} />
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
              value={loggedInUser.otp.provisioning_uri}
              background={theme["--surface"]}
              color={theme["--primary"]}
            />
            <button
              on:click={async () => {
                await navigator.clipboard.writeText(loggedInUser.otp.secret);
              }}
            >
              <i>vpn_key</i>
              <span>Copy secret</span>
            </button>
          </div>
        {/if}

        <OtpInput {onOtpEnter} />
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
