<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link } from "svelte-navigator";
  import { zxcvbn } from "@zxcvbn-ts/core";

  import sodium from "libsodium-wrappers";

  import { themeStore } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import { client } from "../lib/canary";
  import type { Argon2Modal } from "../lib/client";

  export let isRegister = false;

  let mode = isRegister ? "Register" : "Login";
  let passwordScreen = true;
  let captchaToken = "";
  let error = "";

  let email = "";
  let rawPassword = "";
  let rememberLogin = false;

  $: theme = get(themeStore);
  themeStore.subscribe((value) => (theme = value));

  async function onLogin() {
    await sodium.ready;

    error = "";

    if (captchaToken === "") {
      error = "Please complete captcha.";
      return;
    }

    let argon: Argon2Modal;
    let rawSalt: Uint8Array;
    if (!isRegister) {
      argon = await client.account.controllersAccountEmailKdfKdf(email);
      rawSalt = sodium.from_base64(argon.salt);
    } else {
      // Add a bare min for a decent password.
      if (zxcvbn(rawPassword).score < 3) {
        error = "Please use a stronger password.";
        return;
      }

      argon = {
        salt: "",
        time_cost: sodium.crypto_pwhash_OPSLIMIT_SENSITIVE,
        memory_cost: sodium.crypto_pwhash_MEMLIMIT_SENSITIVE,
      };
      rawSalt = sodium.randombytes_buf(sodium.crypto_pwhash_SALTBYTES);
    }

    const rawDerivedKey = sodium.crypto_pwhash(
      32,
      rawPassword,
      rawSalt,
      argon.time_cost,
      argon.memory_cost,
      sodium.crypto_pwhash_ALG_DEFAULT
    );

    console.log(rawDerivedKey);
  }
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

      <form on:submit|preventDefault={onLogin} id="login">
        {#if error !== ""}
          <div class="red5">
            <p>{error}</p>
          </div>
        {/if}
        <div class="field label border medium-divider fill">
          <input type="text" bind:value={email} />
          <label for="email">Email</label>
        </div>
        <div class="field label border medium-divider fill">
          <input type="password" bind:value={rawPassword} />
          <label for="password">Password</label>
        </div>
        {#if isRegister}
          <div class="field label border medium-divider fill">
            <input type="password" />
            <label for="password">Repeat Password</label>
          </div>
        {/if}
        <label class="checkbox">
          <input type="checkbox" bind:checked={rememberLogin} />
          <span>Remember me</span>
        </label>

        <Mcaptcha bind:captchaToken />

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
          <label for="otp">000000</label>
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

  .red5 {
    padding: 0.5em 1em;
    margin-top: 1em;
  }
</style>
