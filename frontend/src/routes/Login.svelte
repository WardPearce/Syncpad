<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link, navigate } from "svelte-navigator";
  import { zxcvbn } from "@zxcvbn-ts/core";

  import sodium from "libsodium-wrappers-sumo";

  import { advanceModeStore, themeStore } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import { client } from "../lib/canary";
  import { type Argon2Modal, type CreateUserModel } from "../lib/client";
  import { timeout } from "../lib/misc";

  export let isRegister = false;

  let mode = isRegister ? "Register" : "Login";
  let otpSetupRequired = false;
  let passwordScreen = true;
  let error = "";
  let advanceModeMsg = "";
  let isLoading = false;

  let email = "";
  let rawPassword = "";
  let captchaToken = "";
  let rememberLogin = false;

  $: theme = get(themeStore);
  themeStore.subscribe((value) => (theme = value));

  $: advanceMode = false;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  async function onLogin() {
    isLoading = true;
    error = "";

    advanceModeMsg = "libsodium blocks :(";
    await timeout(10); // Stop libsodium from blocking loop before updating loading

    await sodium.ready;

    if (captchaToken === "") {
      error = "Please complete captcha.";
      isLoading = false;
      return;
    }

    let argon: Argon2Modal;
    let rawSalt: Uint8Array;
    if (!isRegister) {
      advanceModeMsg = "Fetching account KDF";
      argon = await client.account.controllersAccountEmailKdfKdf(email);
      rawSalt = sodium.from_base64(argon.salt);
    } else {
      // Add a bare min for a decent password.
      if (zxcvbn(rawPassword).score < 3) {
        error = "Please use a stronger password.";
        return;
      }

      try {
        await client.account.controllersAccountEmailKdfKdf(email);
        error = "Email taken.";
        isLoading = false;
        return;
      } catch (error) {}

      advanceModeMsg = "Generating salt.";

      rawSalt = sodium.randombytes_buf(sodium.crypto_pwhash_SALTBYTES);

      argon = {
        salt: sodium.to_base64(rawSalt),
        time_cost: sodium.crypto_pwhash_OPSLIMIT_SENSITIVE,
        memory_cost: sodium.crypto_pwhash_MEMLIMIT_SENSITIVE,
      };
    }

    advanceModeMsg = "Deriving key from password.";
    const rawDerivedKey = sodium.crypto_pwhash(
      32,
      rawPassword,
      rawSalt,
      argon.time_cost,
      argon.memory_cost,
      sodium.crypto_pwhash_ALG_DEFAULT
    );

    advanceModeMsg = "Seeding keypair.";
    const rawAuthKeys = sodium.crypto_sign_seed_keypair(rawDerivedKey);

    if (isRegister) {
      const rawKeychain = sodium.crypto_aead_xchacha20poly1305_ietf_keygen();
      const rawKeychainIv = sodium.randombytes_buf(
        sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES
      );

      const TransmitSafeKeychain = sodium.to_base64(
        sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
          rawKeychain,
          null,
          null,
          rawKeychainIv,
          rawDerivedKey
        )
      );
      const TransmitSafeKeychainIv = sodium.to_base64(rawKeychainIv);

      const createUser: CreateUserModel = {
        email: email,
        kdf: argon,
        keychain: {
          iv: TransmitSafeKeychainIv,
          cipher_text: TransmitSafeKeychain,
        },
        ed25199: {
          public_key: sodium.to_base64(rawAuthKeys.publicKey),
        },
        signature: "",
      };

      createUser.signature = sodium.to_base64(
        sodium.crypto_sign(
          sodium.crypto_generichash(
            sodium.crypto_generichash_BYTES,
            JSON.stringify(createUser)
          ),
          rawAuthKeys.privateKey
        )
      );

      try {
        await client.account.controllersAccountCreateCreateAccount(
          captchaToken,
          createUser
        );
      } catch (error) {
        error = error.body.detail;
        isLoading = false;
        return;
      }

      navigate("/login", { replace: true });
      return;
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
          {#if error}
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
              value="https://github.com/"
              background={theme["--surface"]}
              color={theme["--primary"]}
            />
            <button>
              <i>vpn_key</i>
              <span>Copy secret</span>
            </button>
          </div>
        {/if}

        <nav>
          <div class="max field label fill border">
            <input type="text" />
            <label for="otp">OTP code</label>
          </div>
          <button class="square extra">
            <i>arrow_forward_ios</i>
          </button>
        </nav>
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
    margin-top: 1em;
  }
</style>
