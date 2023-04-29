<script lang="ts">
  import { onMount } from "svelte";

  import { advanceModeStore, themeStore } from "../stores";
  import { getDynamicTheme } from "../lib/theme";

  export let domainName: string;

  let advanceMode: boolean;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  onMount(async () => {
    // To be done based off API.
    await window.ui("theme", "#ffdb57");
    themeStore.set(await getDynamicTheme());
  });
</script>

<article>
  <details>
    <summary class="none">
      <div class="row">
        <img
          class="small"
          src="https://www.privacyguides.org/en/assets/brand/SVG/Logo/privacy-guides-logo-notext-darkbg.svg#only-dark"
        />
        <div class="max">
          <h4>privacyguides.org</h4>
        </div>
        <i>arrow_drop_down</i>
      </div>
    </summary>
    <p>
      Privacy Guides is a socially motivated website that provides information
      for protecting your data security and privacy. Our mission is to inform
      the public about the value of digital privacy, and global government
      initiatives which aim to monitor your online activity. We are a non-profit
      collective operated entirely by volunteer team members and contributors.
      Our website is free of advertisements and not affiliated with any of the
      listed providers.
    </p>

    <h6>Domain ownership</h6>
    <p>
      Verified owner of <a
        href="http://privacyguides.org"
        target="_blank"
        class="link"
        rel="noopener noreferrer">privacyguides.org</a
      >.
    </p>

    <h6>Public key</h6>
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

    <h6>BLAKE2b hash</h6>
    <div class="field textarea border">
      <textarea
        disabled
        value="01fb78393eb2e9e544927cbebc34204b2af88996045bc6ce34d2dbaf693a9a565f4015535aa07ed0fc2b6a35c912a96dbefd0af4fbb0f37631846427b114f54d"
      />
    </div>
  </details>
</article>

<article>
  <nav>
    <h3>Latest Canary</h3>
    <div class="small chip circle">
      <i>done_all</i>
      <div class="tooltip right">
        Cryptographically signed by privacyguides.org
      </div>
    </div>
  </nav>
  <div class="grid">
    <div class="s12 m6 l3">
      <article class="border">
        <div class="row">
          <div class="max">
            <h5>Concern</h5>
            <h6 class="green-text">None</h6>
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

  <h5>Statement</h5>
  <p>
    I hereby declare that as of 28th April 2023, I am still in complete control
    of <a
      href="http://privacyguides.org"
      target="_blank"
      class="link"
      rel="noopener noreferrer">privacyguides.org</a
    > and all its associated data. As the owner and administrator of the website,
    I have not received any subpoenas for data, and I remain committed to protecting
    the privacy and security of all users of my website. This statement will be reviewed
    and updated as necessary on or before 28th April 2024.
  </p>

  <h5>Documents</h5>
  <p>None</p>

  {#if advanceMode}
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

<button class="medium-divider large">View previous statement</button>
