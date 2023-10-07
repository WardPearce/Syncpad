<script lang="ts">
    import { onMount } from "svelte";
    import apiClient from "../../../lib/apiClient";
    import {
        decryptAnswers,
        type rawQuestionAnswer,
    } from "../../../lib/survey";
    import Question from "../Submit/Question.svelte";
    import type { rawSurveyQuestions } from "../types";

    export let surveyId: string;
    export let rawPublicKey: Uint8Array;
    export let rawPrivateKey: Uint8Array;
    export let rawSurveyQuestions: rawSurveyQuestions;

    let currentPage = 0;
    let individualResult: rawQuestionAnswer[] = [];
    let apiError: string = "";

    async function loadResult() {
        individualResult = [];

        let result;
        try {
            result =
                await apiClient.survey.controllersSurveySurveyIdResponsesPageGetResponse(
                    surveyId,
                    currentPage
                );
        } catch (error) {
            apiError = error.body.detail;
            return;
        }

        let resultAnswer: number | number[] | string;
        for (const answer of decryptAnswers(
            rawPublicKey,
            rawPrivateKey,
            result
        )) {
            if (!(answer.answer instanceof Array)) {
                if (!isNaN(Number(answer.answer))) {
                    resultAnswer = Number(answer.answer);
                } else {
                    resultAnswer = answer.answer;
                }
            } else {
                resultAnswer = [];
                answer.answer.forEach((answerId) =>
                    (resultAnswer as number[]).push(Number(answerId))
                );
            }
            individualResult.push({
                id: answer.id,
                type: answer.type,
                answer: resultAnswer,
                regex: rawSurveyQuestions[answer.id].regex,
                error: null,
                description: rawSurveyQuestions[answer.id].description,
                choices: rawSurveyQuestions[answer.id].choices,
                required: rawSurveyQuestions[answer.id].required,
                question: rawSurveyQuestions[answer.id].question,
            });
        }

        individualResult = [...individualResult];
    }

    onMount(async () => {
        await loadResult();
    });
</script>

{#if individualResult.length > 0}
    {#each individualResult as question}
        <Question {...question} answer={question.answer} readOnly={true} />
    {/each}
{:else}
    <article
        class="extra-large-width"
        style="display: flex;justify-content: center; align-items: center;height: 35vh;"
    >
        <h5>{apiError}</h5>
    </article>
{/if}

<div class="pagination extra-large-width">
    {#if currentPage !== 0}
        <button on:click={async () => (currentPage--, await loadResult())}>
            <i>arrow_back</i>
            <span>Past response</span>
        </button>
    {:else}
        <div />
    {/if}
    {#if individualResult.length > 0}
        <button on:click={async () => (currentPage++, await loadResult())}>
            <span>Next response</span>
            <i>arrow_forward</i>
        </button>
    {/if}
</div>
