<script lang="ts">
    import type { ComponentType } from "svelte";
    import Question from "../../../components/Survey/Question.svelte";
    import Title from "../../../components/Survey/Title.svelte";

    let surveyIndex = 0;
    let surveyQuestions: { index: number; component: ComponentType }[] = [];

    addQuestion();

    function addQuestion() {
        surveyQuestions = [
            ...surveyQuestions,
            { index: surveyIndex++, component: Question },
        ];
    }

    function removeQuestion(index: number) {
        surveyQuestions = surveyQuestions.filter(
            (question) => question.index !== index
        );
    }
</script>

<div class="center-questions">
    <Title />

    {#each surveyQuestions as question}
        <svelte:component
            this={question.component}
            {removeQuestion}
            surveyIndex={question.index}
        />
    {/each}

    <button on:click={addQuestion} style="margin-top: 2em;">
        <i>add</i>
        <span>New Question</span>
    </button>
</div>

<style>
    .center-questions {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>
