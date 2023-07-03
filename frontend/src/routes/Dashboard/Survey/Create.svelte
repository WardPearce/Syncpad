<script lang="ts">
    import type { ComponentType } from "svelte";
    import TextArea from "../../../components/Survey/TextArea.svelte";
    import TextInput from "../../../components/Survey/TextInput.svelte";
    import { SurveyComponentsTypes } from "../../../components/Survey/modes";

    let surveyStructure: ComponentType[] = [];

    let surveyTitle = "Untitled Survey";
    let editTitle = false;

    const surveyComponents = [
        { name: "Text area", component: TextArea },
        { name: "Text input", component: TextInput },
    ];

    function addComponent(component: ComponentType) {
        surveyStructure = [...surveyStructure, component];
    }
</script>

{#if !editTitle}
    <nav>
        <h3>{surveyTitle}</h3>
        <button class="square round" on:click={() => (editTitle = true)}>
            <i>create</i>
        </button>
    </nav>
{:else}
    <form on:submit|preventDefault={() => (editTitle = false)}>
        <nav style="margin-top: 1em;">
            <div class="field border">
                <input type="text" bind:value={surveyTitle} />
            </div>
            <button class="square round">
                <i>check</i>
            </button>
        </nav>
    </form>
{/if}

{#each surveyStructure as surveyComp}
    <svelte:component this={surveyComp} mode={SurveyComponentsTypes.preview} />
{/each}

<article class="border no-padding middle-align center-align">
    <div class="padding">
        <button type="button">
            <i>add</i>
            <span>Add question</span>
            <menu>
                {#each surveyComponents as survey}
                    <a
                        href={`#${survey.name}`}
                        on:click={() => addComponent(survey.component)}
                        >{survey.name}</a
                    >
                {/each}
            </menu>
        </button>
    </div>
</article>
