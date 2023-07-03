<script lang="ts">
    import { SurveyComponentsTypes } from "./modes";

    export let mode: SurveyComponentsTypes = SurveyComponentsTypes.preview;
    export let paragraph: string | null = null;
    export let question: string = "Placeholder question";
    export let regex: string | null = null;
    export let value: string = "";
</script>

<article>
    <h5>{question}</h5>
    <div class="field border">
        <input
            type="text"
            disabled={[
                SurveyComponentsTypes.preview,
                SurveyComponentsTypes.result,
            ].includes(mode)}
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
