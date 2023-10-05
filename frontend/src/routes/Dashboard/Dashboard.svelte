<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-navigator";

  import CanaryCard from "../../components/Dashboard/CanaryCard.svelte";
  import SurveyCard from "../../components/Dashboard/SurveyCard.svelte";
  import apiClient from "../../lib/apiClient";
  import type { CanaryModel, SurveyModel } from "../../lib/client";
  import { enabled } from "../../stores";

  let canaries: CanaryModel[] = [];
  let surveys: SurveyModel[] = [];

  onMount(async () => {
    if ($enabled.canaries)
      canaries = await apiClient.canary.controllersCanaryListListCanaries();

    if ($enabled.survey)
      surveys = await apiClient.survey.controllersSurveyListListSurveys();
  });
</script>

{#if $enabled.canaries}
  <h3>Surveys</h3>
  <div class="grid">
    {#if surveys.length > 0}
      {#each surveys as survey}
        <SurveyCard {survey} />
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
{/if}

{#if $enabled.canaries}
  <h3 style="margin-top: 2em;">Canaries</h3>
  <div class="grid">
    {#if canaries.length > 0}
      {#each canaries as canary}
        <CanaryCard {canary} />
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
{/if}
