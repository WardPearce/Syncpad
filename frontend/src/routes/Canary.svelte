<script lang="ts">
  import { onMount } from "svelte";

  import { get } from "svelte/store";
  import PageLoading from "../components/PageLoading.svelte";
  import apiClient from "../lib/apiClient";
  import type { PublicCanaryModel } from "../lib/client";
  import { base64Decode } from "../lib/crypto/codecUtils";
  import { hashBase64Encode } from "../lib/crypto/hash";
  import signatures from "../lib/crypto/signatures";
  import {
    advanceModeStore,
    savedCanaries,
    updateSavedCanaries,
  } from "../stores";

  export let domainName: string;
  export let publicKeyHash: string;

  let advanceMode: boolean;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  let isLoading = true;
  let canaryBioMatches = false;
  let serverKeyHashMatches = false;
  let serverPublicKeyHash: string;
  let canaryBio: PublicCanaryModel;
  onMount(async () => {
    canaryBio =
      await apiClient.canary.controllersCanaryDomainPublicPublicCanary(
        domainName
      );

    const publicServerKey = base64Decode(canaryBio.keypair.public_key);

    serverPublicKeyHash = hashBase64Encode(publicServerKey, true);

    serverKeyHashMatches = serverPublicKeyHash === publicKeyHash;

    if (serverKeyHashMatches) {
      const storedCanaries = get(savedCanaries);
      if (storedCanaries && canaryBio.domain in storedCanaries) {
        serverKeyHashMatches =
          publicKeyHash === storedCanaries[canaryBio.domain].publicKey;
      } else {
        await updateSavedCanaries(canaryBio.domain, {
          id: canaryBio._id,
          publicKey: publicKeyHash,
        });
      }
    }

    try {
      signatures.validateHash(
        publicServerKey,
        canaryBio.signature,
        JSON.stringify({
          domain: canaryBio.domain,
          about: canaryBio.about,
          signature: "",
        })
      );
      canaryBioMatches = true;
    } catch (error) {
      canaryBioMatches = false;
    }

    isLoading = false;
  });
</script>

{#if isLoading}
  <PageLoading />
{:else}
  {#if !serverKeyHashMatches}
    <article class="error">
      <h5>Public key has been tampered with!</h5>
      <p>
        Provided public key from the server, does not match the Public key hash
        in the URL.
      </p>
      <p>
        This is a <span style="font-weight: bold;">significant concern</span>,
        either you have been given an invalid URL or the host is trying to issue
        fake canaries.
      </p>
      <p>
        How to fix? Make sure you are visiting the Canary from a trustworthy
        site.
      </p>
      <h6>
        No canaries issued should be considered trustworthy till this message
        disappears.
      </h6>
    </article>
  {/if}
  {#if !canaryBioMatches}
    <article class="error">
      <h6>The about section failed to be validated!</h6>
      <p>Don't trust the about section or domain name.</p>
    </article>
  {/if}
  <article>
    <details>
      <summary class="none">
        <div class="row canary-name">
          <img
            class="medium"
            src={canaryBio.logo}
            alt={`Logo for ${canaryBio.domain}`}
          />
          <div class="max">
            <h4>{canaryBio.domain}</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <p>
        {canaryBio.about}
      </p>

      <h6>Domain ownership</h6>
      <p>
        Verified owner of <a
          href={`https://${canaryBio.domain}`}
          target="_blank"
          class="link"
          rel="noopener noreferrer">{canaryBio.domain}</a
        >.
      </p>

      {#if advanceMode}
        <div class="field border">
          <input disabled value={canaryBio.keypair.public_key} />
        </div>

        <h6>Hash</h6>
        <div class="field border">
          <input disabled value={serverPublicKeyHash} />
        </div>
      {/if}
    </details>
  </article>

  <article>
    <nav>
      <h3>Latest Canary</h3>
      {#if serverKeyHashMatches}
        <div class="small chip circle">
          <i>done_all</i>
          <div class="tooltip right">
            Cryptographically signed by {canaryBio.domain}
          </div>
        </div>
      {:else}
        <div class="small chip circle error">
          <i>error_outline</i>
          <div class="tooltip right">Unable to validate this Canary.</div>
        </div>
      {/if}
    </nav>
    {#if !serverKeyHashMatches}
      <article class="error">
        <p>This canary failed validation, do NOT trust it.</p>
      </article>
    {:else}
      <div class="grid">
        <div class="s12 m6 l3">
          <article class="border">
            <div class="row">
              <div class="max">
                <h5>Concern</h5>
                <h6 class="deep-purple-text">None</h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l3">
          <article class="border">
            <div class="row">
              <div class="max">
                <h5>Subpoenas</h5>
                <h6>0</h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l3">
          <article class="border">
            <div class="row">
              <div class="max">
                <h5>Issued</h5>
                <h6>28th April 2023</h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l3">
          <article class="border">
            <div class="row">
              <div class="max">
                <h5>Next Canary</h5>
                <h6>In 3 days</h6>
              </div>
            </div>
          </article>
        </div>
      </div>
    {/if}

    <h5>Statement</h5>
    <p class:strikeout={!serverKeyHashMatches}>
      I hereby declare that as of 28th April 2023, I am still in complete
      control of <a
        href="http://privacyguides.org"
        target="_blank"
        class="link"
        rel="noopener noreferrer">privacyguides.org</a
      > and all its associated data. As the owner and administrator of the website,
      I have not received any subpoenas or warrants for data, nor have I received
      any gag order limiting me from informing users as such, and I remain committed
      to protecting the privacy and security of all users of my website. This statement
      will be reviewed and updated as necessary on or before 28th April 2024.
    </p>

    {#if serverKeyHashMatches}
      <h5>Documents</h5>
      <p>None</p>
    {/if}

    {#if advanceMode}
      <h5>Canary ID</h5>
      <div class="field border">
        <input type="text" disabled value="U5bPdJdCaoa3Mw" />
      </div>

      <h5>Server issuer ID</h5>
      <div class="field border">
        <input type="text" disabled value="bDuRLaf2SG5k6aZ6S5U5bPdJdCaoa3Mw" />
      </div>

      <h5>Signature</h5>
      <div class="field textarea border">
        <textarea
          disabled
          value="MIHcAgEBBEIB7dvzJtl2a4NPp482YPFrddA90ATkK438mWCbR54fyx69/oh78ClH
68d9HaC6PvLiWCrOByGgeGjxHbAblavfbEygBwYFK4EEACOhgYkDgYYABAHFgVVQ
dWEkCazcHsNkq2E8dKHtTX2ezA/jLGIimfBHM476LOUNpm9MrlSeZX9+mc4H898y
jLMXUnehpxSJDzRJggChHN8//lTuNBZjrF5At5rKOyIPhOqji5r8owsemRWRc2h3
4xKXQhZ47UFtZs9KvElr1PNGFBivSfwp1mls347j3w=="
        />
      </div>

      <h5>Raw message</h5>
      <div class="field textarea border">
        <textarea disabled value="" />
      </div>
    {/if}
  </article>

  <button class="medium-divider large">View previous cancary</button>
{/if}

<style>
  @media only screen and (max-width: 600px) {
    .canary-name {
      flex-direction: column;
    }
  }
  @media only screen and (max-width: 600px) {
    .canary-name i {
      display: none;
    }
  }

  .strikeout {
    text-decoration: line-through;
  }
</style>
