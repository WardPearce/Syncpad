<script lang="ts">
    import type { ComponentType } from "svelte";
    import { dndzone } from "svelte-dnd-action";

    import Question from "../../../components/Survey/Question.svelte";
    import Title from "../../../components/Survey/Title.svelte";
    import { SurveyAnswerType } from "../../../components/Survey/types";

    let surveyId = 0;
    let surveyQuestions: {
        id: number;
        component: ComponentType;
        regex: string | null;
        required: boolean;
        question: string;
        type: SurveyAnswerType;
    }[] = [];
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
            {
                id: surveyId++,
                component: Question,
                regex: null,
                required: false,
                question: "Untitled Question",
                type: SurveyAnswerType["Short answer"],
            },
        ];
    }

    function duplicateQuestion(index: number) {
        const question = surveyQuestions.find(
            (question) => question.id === index
        );
        if (question) {
            surveyQuestions = [
                ...surveyQuestions,
                {
                    id: surveyId++,
                    component: question.component,
                    regex: question.regex,
                    required: question.required,
                    question: question.question,
                    type: question.type,
                },
            ];
        }
    }

    function removeQuestion(index: number) {
        surveyQuestions = surveyQuestions.filter(
            (question) => question.id !== index
        );
    }

    async function onPublish() {}
</script>

<div class="center-questions">
    <article class="extra-large-width secondary-container">
        <h6>Ensuring Secure and Confidential Survey Data</h6>

        <p>
            All survey questions, answers, and metadata are protected through
            end-to-end encryption. This means that only the individuals who you
            share the link with can view the questions, while the answers remain
            confidential and accessible only to you.
        </p>

        <nav class="right-align">
            <button on:click={onPublish}>
                <i>publish</i>
                <span>Publish</span>
            </button>
        </nav>
    </article>
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
                bind:regex={question.regex}
                bind:required={question.required}
                bind:question={question.question}
                bind:type={question.type}
                {duplicateQuestion}
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
