<script lang="ts">
  import { onMount } from "svelte";
  import { link, navigate } from "svelte-navigator";

  import Image from "../../components/Image.svelte";
  import apiClient from "../../lib/apiClient";
  import { goToCanary } from "../../lib/canary";
  import type { CanaryModel, SurveyModel } from "../../lib/client";
  import secretKey, { SecretkeyLocation } from "../../lib/crypto/secretKey";
  import { concat } from "../../lib/misc";

  let canaries: CanaryModel[] = [];
  let surveys: SurveyModel[] = [];

  function decryptSurveyTitle(survey: SurveyModel): string {
    const rawKey = secretKey.decrypt(
      SecretkeyLocation.localKeychain,
      survey.secret_key.iv,
      survey.secret_key.cipher_text
    ) as Uint8Array;

    return secretKey.decrypt(
      rawKey,
      survey.title.iv,
      survey.title.cipher_text,
      true
    ) as string;
  }

  onMount(async () => {
    canaries = await apiClient.canary.controllersCanaryListListCanaries();
    surveys = await apiClient.survey.controllersSurveyListListSurveys();
  });
</script>

<h3>Surveys</h3>
<div class="grid">
  {#if surveys.length > 0}
    {#each surveys as survey}
      <div class="s12 m6 l4">
        <article>
          <button class="link-button">
            <h6>{decryptSurveyTitle(survey)}</h6>
          </button>
          <nav>
            <button class="border">Edit</button>
          </nav>
        </article>
      </div>
    {/each}
  {/if}
  <div class="s12 m6 l4">
    <article class="border center-align middle-align" style="height: 100%;">
      <a class="button" href="/dashboard/survey/create" use:link>
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
            <Image
              src={`${canary.logo}`}
              size="small"
              alt={`Logo for ${canary.domain}`}
            />
            {#if canary.domain_verification.completed}
              <button on:click={() => goToCanary(canary)} class="link-button">
                <h6>{concat(canary.domain)}</h6>
              </button>
            {:else}
              <h6>{concat(canary.domain)}</h6>
            {/if}
          </div>
          <nav>
            {#if canary.domain_verification.completed}
              <a
                href={`/dashboard/canary/publish/${canary.domain}/`}
                class="button"
                use:link>Publish Canary</a
              >
              <button class="border">Edit</button>
            {:else}
              <button
                on:click={() =>
                  navigate(`/dashboard/canary/verify-site/${canary.domain}/`, {
                    replace: true,
                  })}>Verify domain</button
              >
            {/if}
          </nav>
        </article>
      </div>
    {/each}
  {/if}
  <div class="s12 m6 l4">
    <article class="border center-align middle-align" style="height: 100%;">
      <a class="button" href="/dashboard/canary/add-site" use:link>
        <i>add</i>
        <span>Add Site</span>
      </a>
    </article>
  </div>
</div>
