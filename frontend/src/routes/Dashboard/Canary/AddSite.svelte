<script lang="ts">
  import { link } from "svelte-navigator";
  import apiClient from "../../../lib/apiClient";

  let siteDomain = "";
  let aboutSite = "";
  let siteLogo: File;

  async function createCanary() {
    await apiClient.canary.controllersCanaryCreateCreateCanary({
      domain: siteDomain,
      about: aboutSite,
      keypair: {
        cipher_text: "",
        iv: "",
        public_key: "",
      },
    });
  }
</script>

<h3>Add site</h3>
<div class="field label border" class:invalid={siteDomain.length > 50}>
  <input type="text" bind:value={siteDomain} />
  <label for="domain">Domain name</label>
  <span class="helper">{siteDomain.length}/50</span>
</div>

<div
  class="field textarea label border extra"
  class:invalid={aboutSite.length > 500}
>
  <textarea bind:value={aboutSite} />
  <label for="about">About your site</label>
  <span class="helper">{aboutSite.length}/500</span>
</div>

<nav>
  <div class="field label suffix border">
    <input type="text" />
    <input
      type="file"
      bind:value={siteLogo}
      multiple={false}
      accept="image/png, image/jpeg, image/jpg"
    />
    <label for="logo">Logo</label>
    <i>attach_file</i>
    <span class="helper">Max 5MB - PNG, JPEG</span>
  </div>
</nav>

<div class="right-align" style="margin-top: 1em;">
  <a class="button" href="/dashboard/canary/verify-site/123" use:link>
    <i>arrow_forward_ios</i>
    <span>Next step</span>
  </a>
</div>
