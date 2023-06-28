<script lang="ts">
    import { SurveyComponentsTypes } from "./modes";

    export let mode: SurveyComponentsTypes = SurveyComponentsTypes.preview;
    export let paragraph: string | null = null;
    export let question: string = "Textarea input";
    export let regex: string | null = null;
    export let value: string = "";
</script>

<article class:surface-variant={mode === SurveyComponentsTypes.preview}>
    <h5>{question}</h5>
    <div class="field border">
        <input
            type="text"
            disabled={mode in
                [SurveyComponentsTypes.preview, SurveyComponentsTypes.result]}
            bind:value
        />
        {#if regex}
            <span class="helper">{regex}</span>
        {/if}
    </div>

    {#if paragraph}
        <p>{paragraph}</p>
    {/if}
</article>

<style>
    .field {
        margin: 0;
    }
</style>
