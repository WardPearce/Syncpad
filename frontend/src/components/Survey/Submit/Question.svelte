<script lang="ts">
    import type { SurveyAnswerType } from "../types";
    import MultipleChoice from "./MultipleChoice.svelte";
    import Paragraph from "./Paragraph.svelte";
    import ShortAnswer from "./ShortAnswer.svelte";
    import SingleChoice from "./SingleChoice.svelte";

    export let question: string;
    export let type: SurveyAnswerType;
    export let required: boolean;
    export let choices: string[];
    export let id: number;
    export let description: string | null;
    export let regex: string | null;

    export let answer: string = "";

    const answerTypes = {
        "Short Answer": ShortAnswer,
        Paragraph: Paragraph,
        "Multiple Choice": MultipleChoice,
        "Single Choice": SingleChoice,
    };
</script>

<article class="extra-large-width">
    <h5>{question}</h5>
    {#if description}
        <p>{description}</p>
    {/if}

    <svelte:component this={answerTypes[type]} {choices} bind:answer />

    {#if regex}
        <p>Regex: {regex}</p>
    {/if}
</article>
