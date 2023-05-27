<script lang="ts">
  import sodium from "libsodium-wrappers-sumo";
  import { onMount } from "svelte";
  import { link, navigate } from "svelte-navigator";

  import apiClient from "../../lib/apiClient";
  import type { CanaryModel } from "../../lib/client";
  import { hashBase64Encode } from "../../lib/crypto/hash";
  import secretKey, { SecretkeyLocation } from "../../lib/crypto/secretKey";
  import { concat } from "../../lib/misc";

  let canaries: CanaryModel[] = [];

  onMount(async () => {
    canaries = await apiClient.canary.controllersCanaryListListCanaries();
  });

  function goToCanary(canary: CanaryModel) {
    // Allows us to validate the canaries public by 1st decrypting the private key.
    const canaryPrivateKey = secretKey.decrypt(
      SecretkeyLocation.localKeychain,
      canary.keypair.iv,
      canary.keypair.cipher_text
    );

    const canaryPublicKey = sodium.crypto_sign_ed25519_sk_to_pk(
      canaryPrivateKey as Uint8Array
    );

    const hash = hashBase64Encode(canaryPublicKey, true);
    navigate(`/c/${canary.domain}/${hash}`, { replace: true });
  }
</script>

<h3>Surveys</h3>
<div class="grid">
  <div class="s12 m6 l4">
    <article class="border center-align middle-align" style="height: 100%;">
      <a class="button" href="/dashboard/survery/create" use:link>
        <i>add</i>
        <span>Create survey</span>
      </a>
    </article>
  </div>
</div>

<h3>Canaries</h3>
<div class="grid">
  {#if canaries.length > 0}
    {#each canaries as canary}
      <div class="s12 m6 l4">
        <article>
          <div class="row">
            <img
              class="small circle"
              src={canary.logo}
              alt={`Logo for ${canary.domain}`}
            />
            <div class="max">
              <button on:click={() => goToCanary(canary)} class="link-button">
                <h6>{concat(canary.domain)}</h6>
              </button>
            </div>
          </div>
          <nav>
            <button>Update Canary</button>
            <button class="border">Edit</button>
          </nav>
        </article>
      </div>
    {/each}
  {/if}
  <div class="s12 m6 l4">
    <article class="border center-align middle-align" style="height: 100%;">
      <a class="button" href="/dashboard/canary/add-site" use:link>
        <i>add</i>
        <span>Add site</span>
      </a>
    </article>
  </div>
</div>
