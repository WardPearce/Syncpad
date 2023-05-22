<script lang="ts">
  import { onMount } from "svelte";
  import sodium from "libsodium-wrappers-sumo";
  import { get } from "svelte/store";

  import type { SessionModel } from "../lib/client";
  import { client } from "../lib/canary";
  import { localSecrets } from "../stores";
  import { base64Decode } from "../lib/base64";

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

  onMount(async () => {
    await sodium.ready;

    privateKey = base64Decode(loggedInSecrets.rawKeypair.privateKey);
    publicKey = base64Decode(loggedInSecrets.rawKeypair.publicKey);

    activeSessions = await client.session.controllersSessionGetSessions();
  });
</script>

<h3>Account</h3>

<h4>Sessions</h4>
<p>
  Please note, device & location information is stored encrypted with your
  public key.
</p>
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
        <button>Logout</button>
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
