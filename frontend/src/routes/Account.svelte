<script lang="ts">
  import sodium from "libsodium-wrappers-sumo";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import UAParser from "ua-parser-js";

  import OtpInput from "../components/OtpInput.svelte";
  import account from "../lib/account";
  import apiClient from "../lib/apiClient";
  import type { SessionModel } from "../lib/client";
  import { base64Decode } from "../lib/crypto/codecUtils";
  import { relativeDate } from "../lib/date";
  import { localSecrets, type LocalSecretsModel } from "../stores";

  interface SessionDeviceModel extends SessionModel {
    uaparser: UAParser;
  }

  let activeSessions: SessionDeviceModel[] = [];
  let loggedInSecrets = get(localSecrets) as LocalSecretsModel;

  let privateKey: Uint8Array;
  let publicKey: Uint8Array;

  let otpError = "";

  function decryptSessionInfo(base64CipherText: string): string {
    try {
      return new TextDecoder().decode(
        sodium.crypto_box_seal_open(
          base64Decode(base64CipherText),
          publicKey,
          privateKey
        )
      );
    } catch (error) {
      return "Failed to decrypted";
    }
  }

  async function logoutSession(sessionId: string) {
    if (sessionId === loggedInSecrets.jti) {
      await account.logout();
    } else {
      await apiClient.session.controllersSessionSessionIdInvalidateSession(
        sessionId
      );
      activeSessions = activeSessions.filter((v) => v._id !== sessionId);
    }
  }

  async function logoutAllOther() {
    activeSessions.forEach(async (session) => {
      if (session._id !== loggedInSecrets.jti) {
        await logoutSession(session._id);
      }
    });
  }

  async function resetOtp(otpCode: string) {
    try {
      await apiClient.account.controllersAccountOtpResetResetOtp(otpCode);
      await account.logout();
    } catch (error) {
      otpError = error.body.detail;
    }
  }

  onMount(async () => {
    privateKey = base64Decode(loggedInSecrets.rawKeypair.privateKey);
    publicKey = base64Decode(loggedInSecrets.rawKeypair.publicKey);

    (await apiClient.session.controllersSessionGetSessions()).forEach(
      (session) =>
        activeSessions.push({
          uaparser: new UAParser(decryptSessionInfo(session.device as string)),
          ...session,
        })
    );

    activeSessions = activeSessions;
  });
</script>

<h3>Account</h3>
<article>
  <h5>Change password</h5>
</article>
<article>
  <h5>OTP reset</h5>
  <p>Enter your current OTP code to reset it.</p>
  <div style="display: flex;">
    {#if otpError}
      <p>{otpError}</p>
    {/if}

    <OtpInput onOtpEnter={resetOtp} />
  </div>
</article>
<article>
  <h5>Login IP processing</h5>
  <p>
    Upon logging in, we utilize your IP address to provide you with details
    about the active session and their location. It is important to acknowledge
    that all device and location information is securely encrypted using your
    public key. This information can only be accessed by you once you have
    successfully logged in.
  </p>
  <p>
    We employ <a
      href="https://proxycheck.io/"
      target="_blank"
      class="link"
      rel="noopener noreferrer">proxycheck.io</a
    > to process your IP address; however, it's important to note that they cannot
    establish a direct correlation between IPs and user accounts.
  </p>
  <label class="switch">
    <input type="checkbox" checked={true} />
    <span />
  </label>
</article>
<article>
  <h5>Danger zone</h5>
  <nav class="wrap">
    <button class="secondary">Rotate keychain</button>
    <button class="tertiary">Delete account</button>
  </nav>
</article>

<h3>Sessions</h3>

{#if activeSessions.length === 0}
  <span class="loader medium" />
{:else}
  {#if activeSessions.length > 1}
    <button on:click={logoutAllOther}>Logout all other sessions</button>
  {/if}

  {#each activeSessions as session}
    <article class:primary-container={session._id === loggedInSecrets.jti}>
      <div class="grid">
        <div class="s12 m6 l3">
          <h6>Location</h6>
          <p>
            <span style="font-weight: bold;">Country:</span>
            {#if session.location.country}
              {decryptSessionInfo(session.location.country)}
            {:else}
              Unknown
            {/if}
          </p>
          <p>
            <span style="font-weight: bold;">Region:</span>
            {#if session.location.region}
              {decryptSessionInfo(session.location.region)}
            {:else}
              Unknown
            {/if}
          </p>
          <p>
            <span style="font-weight: bold;">IP Address:</span>
            {#if session.location.ip}
              {decryptSessionInfo(session.location.ip)}
            {:else}
              Unknown
            {/if}
          </p>
        </div>
        <div class="s12 m6 l3">
          <h6>Device</h6>
          <p>
            <span style="font-weight: bold;">Browser:</span>
            {session.uaparser.getBrowser().name}
          </p>
          <p>
            <span style="font-weight: bold;">Engine:</span>
            {session.uaparser.getEngine().name}
          </p>
          <p>
            <span style="font-weight: bold;">OS:</span>
            {session.uaparser.getOS().name}
          </p>
        </div>
        <div class="s12 m6 l3">
          <h6>Expires</h6>
          <p>
            {relativeDate(session.expires)}
          </p>
        </div>
        <div class="s12 m6 l3">
          <button on:click={async () => await logoutSession(session._id)}
            >Logout
            {#if session._id === loggedInSecrets.jti}
              current session
            {/if}
          </button>
        </div>
      </div>
    </article>
  {/each}
{/if}

<style>
  h6 {
    margin: 0;
    font-size: 1.6em;
  }

  .s12 p {
    margin: 0;
  }

  .s12 {
    display: flex;
    flex-direction: column;
  }
</style>
