<script lang="ts">
  import { onMount } from "svelte";

  import { navigate } from "svelte-navigator";
  import PageLoading from "../components/PageLoading.svelte";
  import apiClient from "../lib/apiClient";
  import { getTrustedCanary, saveCanaryAsTrusted } from "../lib/canary";
  import type { PublicCanaryModel } from "../lib/client";
  import { base64Decode } from "../lib/crypto/codecUtils";
  import { hashBase64Encode } from "../lib/crypto/hash";
  import signatures from "../lib/crypto/signatures";
  import { advanceModeStore } from "../stores";

  export let domainName: string;
  export let publicKeyHash: string;

  let advanceMode: boolean;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  let isLoading = true;
  let canaryBioMatches = false;
  let serverKeyHashMatches = false;
  let firstCanaryVisit = true;
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

    const trustedStoredPublicKeyHash = await getTrustedCanary(domainName);
    if (trustedStoredPublicKeyHash) {
      firstCanaryVisit = false;
    }

    if (serverKeyHashMatches) {
      // Validate stored canary.
      if (trustedStoredPublicKeyHash) {
        serverKeyHashMatches = publicKeyHash === trustedStoredPublicKeyHash;
      } else {
        // Store canary
        await saveCanaryAsTrusted(domainName, publicKeyHash);
      }
    } else if (trustedStoredPublicKeyHash === serverPublicKeyHash) {
      // If stored publicKey hash matches serverPublicKeyHash, then incorrect link was given.
      serverKeyHashMatches = true;
      publicKeyHash = trustedStoredPublicKeyHash;

      navigate(`/c/${domainName}/${trustedStoredPublicKeyHash}`, {
        replace: true,
      });
    } else {
      canaryBioMatches = false;
    }

    // This may change from the above logic.
    if (serverKeyHashMatches) {
      try {
        signatures.validateHash(
          publicServerKey,
          canaryBio.signature,
          JSON.stringify({
            domain: domainName,
            about: canaryBio.about,
            signature: "",
          })
        );
        canaryBioMatches = true;
      } catch (error) {
        canaryBioMatches = false;
      }
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
        the host may be trying to issue fake canaries.
      </p>
    </article>
    {#if firstCanaryVisit}
      <article class="error">
        <h6>Please note</h6>
        <p>
          If you were given an invalid link, this alert would be triggered
          during your first visit to this canary. Please ensure you got this
          link off a trustworthy source.
        </p>
      </article>
    {/if}
  {:else if firstCanaryVisit}
    <article class="primary">
      Welcome to {canaryBio.domain}'s canary! This is your first visit on this
      browser/account, and we've saved it as a trusted canary.
    </article>
  {/if}
  {#if !canaryBioMatches}
    <article class="error">
      <h6>Canary information failed validation!</h6>
      <p>
        This is <span style="font-weight: bold;">concerning</span> & may mean the
        host is trying to trick you.
      </p>
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
            <h4 class:strikeout={!canaryBioMatches}>{canaryBio.domain}</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <p class:strikeout={!canaryBioMatches}>
        {canaryBio.about}
      </p>

      <h6>Domain ownership</h6>
      <p class:strikeout={!canaryBioMatches}>
        Verified owner of <a
          href={`https://${canaryBio.domain}`}
          target="_blank"
          class="link"
          rel="noopener noreferrer">{canaryBio.domain}</a
        >.
      </p>

      {#if advanceMode}
        <h6>Public key</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={canaryBio.keypair.public_key} />
        </div>

        <h6>Hash</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={serverPublicKeyHash} />
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
    {#if !serverKeyHashMatches || !canaryBioMatches}
      <article class="error">
        <p>This canary failed validation, do NOT trust it.</p>
      </article>
    {:else}
      <div class="grid">
        <div class="s12 m6 l4">
          <article class="border surface-variant">
            <div class="row">
              <div class="max">
                <h5>Concern</h5>
                <h6>None</h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l4">
          <article class="border surface-variant">
            <div class="row">
              <div class="max">
                <h5>Issued</h5>
                <h6>28th April 2023</h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l4">
          <article class="border surface-variant">
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
    <p class:strikeout={!serverKeyHashMatches || !canaryBioMatches}>
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

    {#if serverKeyHashMatches && canaryBioMatches}
      <h5>Documents</h5>
      <p>None</p>
    {/if}

    {#if advanceMode}
      <h5>Canary ID</h5>
      <div class="field border" style="margin-top: 0;">
        <input type="text" readonly value="U5bPdJdCaoa3Mw" />
      </div>

      <h5>Signature</h5>
      <div class="field textarea border" style="margin-top: 0;">
        <textarea
          readonly
          value="MIHcAgEBBEIB7dvzJtl2a4NPp482YPFrddA90ATkK438mWCbR54fyx69/oh78ClH
68d9HaC6PvLiWCrOByGgeGjxHbAblavfbEygBwYFK4EEACOhgYkDgYYABAHFgVVQ
dWEkCazcHsNkq2E8dKHtTX2ezA/jLGIimfBHM476LOUNpm9MrlSeZX9+mc4H898y
jLMXUnehpxSJDzRJggChHN8//lTuNBZjrF5At5rKOyIPhOqji5r8owsemRWRc2h3
4xKXQhZ47UFtZs9KvElr1PNGFBivSfwp1mls347j3w=="
        />
      </div>

      <h5>Raw message</h5>
      <div class="field textarea border" style="margin-top: 0;">
        <textarea readonly value="" />
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
