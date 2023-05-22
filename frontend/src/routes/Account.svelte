<script lang="ts">
  import { onMount } from "svelte";
  import sodium from "libsodium-wrappers-sumo";
  import { get } from "svelte/store";

  import type { SessionModel } from "../lib/client";
  import { client } from "../lib/canary";
  import { localSecrets } from "../stores";
  import { base64Decode } from "../lib/base64";
  import { logout } from "../lib/logout";

  let activeSessions: SessionModel[] = [];
  let loggedInSecrets = get(localSecrets);

  let privateKey: Uint8Array;
  let publicKey: Uint8Array;

  function decryptInfo(base64CipherText: string): string {
    return new TextDecoder().decode(
      sodium.crypto_box_seal_open(
        base64Decode(base64CipherText),
        publicKey,
        privateKey
      )
    );
  }

  async function logoutSession(sessionId: string) {
    activeSessions = activeSessions.filter((v) => v._id !== sessionId);
    await client.session.controllersSessionSessionIdInvalidateSession(
      sessionId
    );
    if (sessionId === loggedInSecrets.jti) {
      await logout();
    }
  }

  onMount(async () => {
    await sodium.ready;

    privateKey = base64Decode(loggedInSecrets.rawKeypair.privateKey);
    publicKey = base64Decode(loggedInSecrets.rawKeypair.publicKey);

    activeSessions = await client.session.controllersSessionGetSessions();
  });
</script>

<h3>Account</h3>
<article style="margin-top: 1em;">
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

<h4>Sessions</h4>

{#if activeSessions.length === 0}
  <span class="loader medium" />
{:else}
  {#each activeSessions as session}
    <article>
      <div class="max">
        <h5>
          {session._id}
        </h5>
        {#if session._id === loggedInSecrets.jti}
          <p class="green-text">Current session</p>
        {/if}
        <h6>Expires</h6>
        <p>
          {session.expires}
        </p>
        <h6>Device</h6>
        <p>
          {decryptInfo(session.device)}
        </p>
        <h6>Location</h6>
        <p>
          <span style="font-weight: bold;">Country:</span>
          {#if session.location.country}
            {decryptInfo(session.location.country)}
          {:else}
            Unknown
          {/if}
        </p>
        <p>
          <span style="font-weight: bold;">Region:</span>
          {#if session.location.region}
            {decryptInfo(session.location.region)}
          {:else}
            Unknown
          {/if}
        </p>
        <p>
          <span style="font-weight: bold;">IP Address:</span>
          {#if session.location.ip}
            {decryptInfo(session.location.ip)}
          {:else}
            Unknown
          {/if}
        </p>
      </div>
      <div class="right-align" style="margin-top: 1em;">
        <button on:click={async () => await logoutSession(session._id)}
          >Logout</button
        >
      </div>
    </article>
  {/each}
{/if}

<style>
  h6 {
    margin: 0;
    font-size: 1.6em;
  }
</style>
