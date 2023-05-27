<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-navigator";

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
