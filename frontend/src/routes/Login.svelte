<script lang="ts">
  import QrCode from "svelte-qrcode";
  import { get } from "svelte/store";
  import { link, navigate, useLocation } from "svelte-navigator";
  import { zxcvbn } from "@zxcvbn-ts/core";

  import sodium from "libsodium-wrappers-sumo";

  import {
    advanceModeStore,
    setLocalSecrets,
    localSecrets,
    themeStore,
  } from "../stores";
  import Mcaptcha from "../components/Mcaptcha.svelte";
  import { client } from "../lib/canary";
  import {
    type CreateUserModel,
    type PublicUserModel,
    type UserJtiModel,
  } from "../lib/client";
  import { timeout } from "../lib/misc";
  import { base64Decode, base64Encode } from "../lib/base64";
  import { onMount } from "svelte";
  import OtpInput from "../components/OtpInput.svelte";

  export let isRegister = false;

  $: mode = isRegister ? "Register" : "Login";
  let otpSetupRequired = false;
  let passwordScreen = true;
  let errorMsg = "";
  let advanceModeMsg = "";
  let isLoading = false;

  let redirectPath: string | undefined = get(useLocation()).state.redirect;

  let email = "";
  let rawPassword = "";
  let captchaToken = "";

  let rawAuthKeys: sodium.KeyPair;
  let rawDerivedKey: Uint8Array;
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

  async function attemptAuthorization(otpCode?: string) {
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
          _id: toProve._id,
          signature: base64Encode(
            sodium.crypto_sign(toProve.to_sign, rawAuthKeys.privateKey)
          ),
        },
        otpSetupRequired ? "" : otpCode
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
          time_cost: loggedInUser.user.kdf.time_cost,
          memory_cost: loggedInUser.user.kdf.memory_cost,
          salt: loggedInUser.user.kdf.salt,
        },
        keychain: {
          iv: loggedInUser.user.keychain.iv,
          cipher_text: loggedInUser.user.keychain.cipher_text,
        },
        auth: {
          // Should never be loaded from the server.
          public_key: base64Encode(rawAuthKeys.publicKey),
        },
        keypair: {
          cipher_text: loggedInUser.user.keypair.cipher_text,
          iv: loggedInUser.user.keypair.iv,
          public_key: loggedInUser.user.keypair.public_key,
        },
        signature: "",
      } as CreateUserModel)
    );

    try {
      if (
        sodium.to_hex(
          sodium.crypto_sign(accountHash, rawAuthKeys.privateKey).slice(64)
        ) !==
        sodium.to_hex(
          sodium.crypto_sign_open(
            base64Decode(loggedInUser.user.signature),
            rawAuthKeys.publicKey
          )
        )
      ) {
        throw "Failed to validate given data from server";
      }
    } catch {
      throw "Failed to validate given data from server";
    }

    advanceModeMsg = "Decrypting keychain";

    const rawKeychain = sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
      null,
      base64Decode(loggedInUser.user.keychain.cipher_text),
      null,
      base64Decode(loggedInUser.user.keychain.iv),
      rawDerivedKey
    );

    const rawKeypairPrivateKey =
      sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
        null,
        base64Decode(loggedInUser.user.keypair.cipher_text),
        null,
        base64Decode(loggedInUser.user.keypair.iv),
        rawKeychain
      );

    // Should never store derivedKey or private key.
    // If IndexDB compromised, authorization can't be acquired.
    await setLocalSecrets({
      email: loggedInUser.user.email,
      userId: loggedInUser.user._id,
      rawKeychain: base64Encode(rawKeychain),
      rawKeypair: {
        privateKey: base64Encode(rawKeypairPrivateKey),
        publicKey: loggedInUser.user.keypair.public_key,
      },
      jti: loggedInUser.jti,
    });
  }

  async function OnOtpEnter(otpCode: string) {
    isLoading = true;
    errorMsg = "";

    advanceModeMsg = "Validating OTP code";

    if (otpSetupRequired) {
      try {
        await client.account.controllersAccountOtpSetupOtpSetup(otpCode);
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

    advanceModeMsg = "Seeding auth keypair.";
    rawAuthKeys = sodium.crypto_sign_seed_keypair(rawDerivedKey);

    if (isRegister) {
      advanceModeMsg = "Generating keychain";
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

      advanceModeMsg = "Creating keypair";
      let rawKeypair = sodium.crypto_box_keypair();

      const rawKeypairIv = sodium.randombytes_buf(
        sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES
      );
      const TransmitSafeKeypairPrivate = base64Encode(
        sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
          rawKeypair.privateKey,
          null,
          null,
          rawKeypairIv,
          rawKeychain
        )
      );
      const TransmitSafeKeypairIv = base64Encode(rawKeypairIv);

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
        auth: {
          public_key: base64Encode(rawAuthKeys.publicKey),
        },
        keypair: {
          cipher_text: TransmitSafeKeypairPrivate,
          iv: TransmitSafeKeypairIv,
          public_key: base64Encode(rawKeypair.publicKey),
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
