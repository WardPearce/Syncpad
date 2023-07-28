<script lang="ts">
    import type { SurveyQuestionModel } from "../../../lib/client";
    import type { rawChoice } from "../types";
    import MultipleChoice from "./MultipleChoice.svelte";
    import Paragraph from "./Paragraph.svelte";
    import ShortAnswer from "./ShortAnswer.svelte";
    import SingleChoice from "./SingleChoice.svelte";

    export let question: string;
    export let type: SurveyQuestionModel.type;
    export let required: boolean;
    export let choices: rawChoice[];
    export let id: number;
    export let description: string | null;
    export let regex: string | null;
    export let error: string | null;

    export let answer: number | number[] | string | null;

    const answerTypes = {
        0: ShortAnswer,
        1: Paragraph,
        2: MultipleChoice,
        3: SingleChoice,
    };
</script>

<article class="extra-large-width">
    {#if error}
        <article class="error">
            <span>{error}</span>
        </article>
    {/if}

    <h5>
        {question}
        {#if required}
            <span class="error-text" style="margin-left: .3em;">*</span>
        {/if}
    </h5>

    {#if description}
        <p>{description}</p>
    {/if}

    <svelte:component this={answerTypes[type]} {choices} bind:answer />

    {#if regex}
        <p>Regex: {regex}</p>
    {/if}
</article>
