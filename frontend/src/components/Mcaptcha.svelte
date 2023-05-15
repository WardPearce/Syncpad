<script lang="ts">
  import { gen_pow } from "@mcaptcha/pow-wasm";

  export let captchaToken: string = "";

  $: {
    if (captchaToken === "") status = CaptchaStatus.waiting;
  }

  enum CaptchaStatus {
    waiting = 0,
    loading = 1,
    completed = 2,
  }

  let status = CaptchaStatus.waiting;

  async function startPow() {
    status = CaptchaStatus.loading;

    const configResp = await fetch(
      `${import.meta.env.VITE_MCAPTCHA_API}/pow/config`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify({ key: import.meta.env.VITE_MCAPTCHA_SITE_KEY }),
      }
    );
    // Assume API is down, mark as completed.
    if (configResp.status != 200) {
      status = CaptchaStatus.completed;
      return;
    }

    const configJson = await configResp.json();

    const work = JSON.parse(
      gen_pow(configJson.salt, configJson.string, configJson.difficulty_factor)
    );

    const verifyResp = await fetch(
      `${import.meta.env.VITE_MCAPTCHA_API}/pow/verify`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify({
          key: import.meta.env.VITE_MCAPTCHA_SITE_KEY,
          string: configJson.string,
          ...work,
        }),
      }
    );

    if (verifyResp.status != 200) {
      status = CaptchaStatus.completed;
      return;
    }

    const verifyJson = await verifyResp.json();

    captchaToken = verifyJson.token;

    status = CaptchaStatus.completed;
  }
</script>

<div class="main">
  <div class="captcha">
    {#if status == CaptchaStatus.waiting}
      <button class="square small" on:click={startPow} type="button" />
      <p>I'm not a robot</p>
    {:else if status == CaptchaStatus.loading}
      <span class="loader small" style="margin: 0 1em" />
      <p>Processing</p>
    {:else}
      <button class="square small" disabled type="button">
        <i>check</i>
      </button>
      <p>Captcha completed!</p>
    {/if}
  </div>
  <div class="footer">
    <a
      href="https://github.com/mCaptcha/mCaptcha"
      target="_blank"
      rel="noopener noreferrer"
      class="link">Powered by mCaptcha</a
    >
  </div>
</div>

<style>
  .main {
    background-color: var(--inverse-on-surface);
    margin-top: 1em;
    position: relative;
  }

  .footer {
    position: absolute;
    bottom: 0;
    right: 0;
    font-size: 0.7em;
    margin-right: 0.4em;
    margin-bottom: 0.4em;
  }

  .captcha {
    display: flex;
    align-items: center;
    padding: 1.3em 0.5em;
  }
</style>
