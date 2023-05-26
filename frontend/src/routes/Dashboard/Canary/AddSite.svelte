<script lang="ts">
  import { navigate } from "svelte-navigator";

  import apiClient from "../../../lib/apiClient";
  import type { CreateCanaryModel } from "../../../lib/client";
  import { base64Encode } from "../../../lib/crypto/codecUtils";
  import secretKey, { SecretkeyLocation } from "../../../lib/crypto/secretKey";
  import signatures from "../../../lib/crypto/signatures";

  let siteDomain = "";
  let aboutSite = "";
  let logoFiles: FileList;

  let errorMsg = "";
  let isLoading = false;

  async function createCanary() {
    isLoading = true;
    errorMsg = "";
    const keyPair = signatures.generateKeypair();
    const safePrivateKey = secretKey.encrypt(
      SecretkeyLocation.localKeychain,
      keyPair.privateKey
    );

    const canaryData: CreateCanaryModel = {
      domain: siteDomain,
      about: aboutSite,
      keypair: {
        cipher_text: safePrivateKey.cipherText,
        iv: safePrivateKey.iv,
        public_key: base64Encode(keyPair.publicKey),
      },
      signature: "",
    };

    canaryData.signature = signatures.signHash(
      keyPair.privateKey,
      JSON.stringify(canaryData)
    );

    try {
      await apiClient.canary.controllersCanaryCreateCreateCanary(canaryData);
    } catch (error) {
      errorMsg = error.body.detail;
      isLoading = false;
      return;
    }

    try {
      await apiClient.canary.controllersCanaryDomainLogoUpdateUpdateLogo(
        siteDomain,
        [logoFiles[0]]
      );
    } catch (error) {}
    isLoading = false;
    navigate(`/dashboard/canary/verify-site/${siteDomain}`, { replace: true });
  }
</script>

<h3>Add site</h3>
<form on:submit|preventDefault={createCanary}>
  <div class="field label border" class:invalid={siteDomain.length > 50}>
    <input type="text" bind:value={siteDomain} disabled={isLoading} />
    <label for="domain">Domain name</label>
    <span class="helper">{siteDomain.length}/50</span>
  </div>

  <div
    class="field textarea label border extra"
    class:invalid={aboutSite.length > 500}
  >
    <textarea bind:value={aboutSite} disabled={isLoading} />
    <label for="about">About your site</label>
    <span class="helper">{aboutSite.length}/500</span>
  </div>

  <nav>
    <div class="field label suffix border">
      <input type="text" />
      <input
        type="file"
        bind:files={logoFiles}
        multiple={false}
        accept="image/png, image/jpeg, image/jpg"
      />
      <label for="logo">Logo</label>
      <i>attach_file</i>
      <span class="helper">Max 5MB - PNG, JPEG</span>
    </div>
  </nav>

  <div class="right-align" style="margin-top: 1em;">
    {#if isLoading}
      <span class="loader medium" />
    {:else}
      <button>
        <i>arrow_forward_ios</i>
        <span>Next step</span>
      </button>
    {/if}
  </div>
</form>
