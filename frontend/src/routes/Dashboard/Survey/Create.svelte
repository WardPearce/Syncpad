<script lang="ts">
    import type { ComponentType } from "svelte";
    import { dndzone } from "svelte-dnd-action";

    import Question from "../../../components/Survey/Question.svelte";
    import Title from "../../../components/Survey/Title.svelte";

    let surveyId = 0;
    let surveyQuestions: { id: number; component: ComponentType }[] = [];
    let dragDisabled = true;

    addQuestion();

    function startDrag() {
        dragDisabled = false;
    }

    function stopDrag() {
        dragDisabled = true;
    }

    function handleConsider(event) {
        surveyQuestions = event.detail.items;
    }

    function handleFinalize(event) {
        surveyQuestions = event.detail.items;
        dragDisabled = true;
    }

    function addQuestion() {
        surveyQuestions = [
            ...surveyQuestions,
            { id: surveyId++, component: Question },
        ];
    }

    function removeQuestion(index: number) {
        surveyQuestions = surveyQuestions.filter(
            (question) => question.id !== index
        );
    }
</script>

<div class="center-questions">
    <Title />

    <div
        use:dndzone={{
            items: surveyQuestions,
            dragDisabled: dragDisabled,
            morphDisabled: true,
            dropTargetClasses: ["drop-target"],
        }}
        on:consider={handleConsider}
        on:finalize={handleFinalize}
        style="margin-top: 1em;"
    >
        {#each surveyQuestions as question (question.id)}
            <svelte:component
                this={question.component}
                surveyId={question.id}
                {removeQuestion}
                {startDrag}
                {stopDrag}
            />
        {/each}
    </div>

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
