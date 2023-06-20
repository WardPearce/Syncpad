<script lang="ts">
  import { onMount } from "svelte";
  import { link, navigate } from "svelte-navigator";

  import Image from "../../components/Image.svelte";
  import apiClient from "../../lib/apiClient";
  import { goToCanary } from "../../lib/canary";
  import type { CanaryModel } from "../../lib/client";
  import { concat } from "../../lib/misc";

  let canaries: CanaryModel[] = [];

  onMount(async () => {
    canaries = await apiClient.canary.controllersCanaryListListCanaries();
  });
</script>

<h3>Surveys</h3>
<div class="grid">
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
