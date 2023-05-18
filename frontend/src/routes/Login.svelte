<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link, navigate } from "svelte-navigator";
  import { zxcvbn } from "@zxcvbn-ts/core";

  import sodium from "libsodium-wrappers-sumo";

  import { advanceModeStore, setLocalSecrets, themeStore } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import { client } from "../lib/canary";
  import {
    type CreateUserModel,
    type PublicUserModel,
    type UserModel,
  } from "../lib/client";
  import { timeout } from "../lib/misc";
  import { base64Decode, base64Encode } from "../lib/base64";

  export let isRegister = false;

  $: mode = isRegister ? "Register" : "Login";
  let otpSetupRequired = false;
  let passwordScreen = true;
  let errorMsg = "";
  let advanceModeMsg = "";
  let isLoading = false;

  let email = "";
  let rawPassword = "";
  let captchaToken = "";
  let optCode = "";

  let rawAuthKeys: sodium.KeyPair;
  let rawDerivedKey: Uint8Array;
  let loggedInUser: UserModel;

  $: theme = get(themeStore);
  themeStore.subscribe((value) => (theme = value));

  $: advanceMode = false;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  async function attemptAuthorization() {
    advanceModeMsg = "Getting data to sign";

    const toProve = await client.account.controllersAccountEmailToSignToSign(
      email
    );

    advanceModeMsg = "Sending signed data to server";
    try {
      loggedInUser = await client.account.controllersAccountEmailLoginLogin(
        captchaToken,
        email,
        {
          _id: toProve.id,
          signature: base64Encode(
            sodium.crypto_sign(toProve.to_sign, rawAuthKeys.privateKey)
          ),
        },
        otpSetupRequired ? "" : optCode
      );
    } catch (error) {
      throw error.body.detail;
    }

    // Manually defining the whole object, must
    // be in the same order as the createUser var
    // for hashes to match.
    const accountHash = sodium.crypto_generichash(
      sodium.crypto_generichash_BYTES,
      JSON.stringify({
        email: email,
        kdf: {
          time_cost: loggedInUser.kdf.time_cost,
          memory_cost: loggedInUser.kdf.memory_cost,
          salt: loggedInUser.kdf.salt,
        },
        keychain: {
          iv: loggedInUser.keychain.iv,
          cipher_text: loggedInUser.keychain.cipher_text,
        },
        ed25199: {
          // Should never be loaded from the server.
          public_key: base64Encode(rawAuthKeys.publicKey),
        },
        signature: "",
      })
    );

    try {
      if (
        sodium.to_hex(
          sodium.crypto_sign(accountHash, rawAuthKeys.privateKey).slice(64)
        ) !==
        sodium.to_hex(
          sodium.crypto_sign_open(
            base64Decode(loggedInUser.signature),
            rawAuthKeys.publicKey
          )
        )
      ) {
        throw "Failed to validate given data from server";
      }
    } catch {
      throw "Failed to validate given data from server";
    }

    advanceModeMsg = "Decrypting keychain key";

    const rawKeychain = sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
      null,
      base64Decode(loggedInUser.keychain.cipher_text),
      null,
      base64Decode(loggedInUser.keychain.iv),
      rawDerivedKey
    );

    // Should never store derivedKey or private key.
    // If IndexDB compromised, authorization can't be acquired.
    await setLocalSecrets({
      email: loggedInUser.email,
      userId: loggedInUser.id,
      rawKeychain: base64Encode(rawKeychain),
    });
  }

  async function OnOtpEnter() {
    isLoading = true;
    errorMsg = "";

    advanceModeMsg = "Validating OTP code";

    if (otpSetupRequired) {
      try {
        await client.account.controllersAccountEmailSetupOtpOtpSetup(
          loggedInUser.email,
          optCode
        );
      } catch (error) {
        errorMsg = error.body.detail;
        isLoading = false;
        return;
      }
    } else {
      try {
        await attemptAuthorization();
      } catch (error) {
        errorMsg = error;
        passwordScreen = true;
        rawPassword = "";
        optCode = "";
        isLoading = false;
        return;
      }
    }

    navigate("/dashboard", { replace: true });

    isLoading = false;
  }

  async function onLogin() {
    isLoading = true;
    errorMsg = "";

    advanceModeMsg = "libsodium blocks :(";
    await timeout(10); // Stop libsodium from blocking loop before updating loading

    await sodium.ready;

    if (captchaToken === "") {
      errorMsg = "Please complete captcha.";
      isLoading = false;
      return;
    }

    let rawSalt: Uint8Array;
    let publicUser: PublicUserModel;

    if (!isRegister) {
      advanceModeMsg = "Fetching account KDF parameters";
      publicUser = await client.account.controllersAccountEmailPublicPublic(
        email
      );
      rawSalt = base64Decode(publicUser.kdf.salt);
    } else {
      // Add a bare min for a decent password.
      if (zxcvbn(rawPassword).score < 3) {
        errorMsg = "Please use a stronger password.";
        isLoading = false;
        return;
      }

      try {
        await client.account.controllersAccountEmailPublicPublic(email);
        errorMsg = "Email taken.";
        isLoading = false;
        return;
      } catch (error) {}

      advanceModeMsg = "Generating salt.";

      rawSalt = sodium.randombytes_buf(sodium.crypto_pwhash_SALTBYTES);

      publicUser = {
        kdf: {
          salt: base64Encode(rawSalt),
          time_cost: sodium.crypto_pwhash_OPSLIMIT_SENSITIVE,
          memory_cost: sodium.crypto_pwhash_MEMLIMIT_SENSITIVE,
        },
      };
    }

    advanceModeMsg = "Deriving key from password.";
    rawDerivedKey = sodium.crypto_pwhash(
      32,
      rawPassword,
      rawSalt,
      publicUser.kdf.time_cost,
      publicUser.kdf.memory_cost,
      sodium.crypto_pwhash_ALG_DEFAULT
    );

    advanceModeMsg = "Seeding keypair.";
    rawAuthKeys = sodium.crypto_sign_seed_keypair(rawDerivedKey);

    if (isRegister) {
      const rawKeychain = sodium.crypto_aead_xchacha20poly1305_ietf_keygen();
      const rawKeychainIv = sodium.randombytes_buf(
        sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES
      );

      const TransmitSafeKeychain = base64Encode(
        sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
          rawKeychain,
          null,
          null,
          rawKeychainIv,
          rawDerivedKey
        )
      );
      const TransmitSafeKeychainIv = base64Encode(rawKeychainIv);

      const createUser: CreateUserModel = {
        email: email,
        kdf: {
          time_cost: publicUser.kdf.time_cost,
          memory_cost: publicUser.kdf.memory_cost,
          salt: publicUser.kdf.salt,
        },
        keychain: {
          iv: TransmitSafeKeychainIv,
          cipher_text: TransmitSafeKeychain,
        },
        ed25199: {
          public_key: base64Encode(rawAuthKeys.publicKey),
        },
        signature: "",
      };

      createUser.signature = base64Encode(
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
        errorMsg = error.body.detail;
        isLoading = false;
        return;
      }

      rawPassword = "";
      isRegister = false;
    } else {
      if (!publicUser.otp_completed) {
        try {
          await attemptAuthorization();
        } catch (error) {
          errorMsg = error;
          isLoading = false;
          return;
        }
        otpSetupRequired = true;
      } else {
        otpSetupRequired = false;
      }

      passwordScreen = false;
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

        <form on:submit|preventDefault={OnOtpEnter}>
          <nav>
            <div class="max field label fill border">
              <input type="text" bind:value={optCode} />
              <label for="otp">OTP code</label>
            </div>
            <button class="square extra">
              <i>arrow_forward_ios</i>
            </button>
          </nav>
        </form>
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
