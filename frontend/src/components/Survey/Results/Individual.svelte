<script lang="ts">
    import { onMount } from "svelte";
    import apiClient from "../../../lib/apiClient";
    import {
        decryptAnswers,
        type rawQuestionAnswer,
    } from "../../../lib/survey";
    import type { rawSurveyQuestions } from "../types";

    export let surveyId: string;
    export let rawPublicKey: Uint8Array;
    export let rawPrivateKey: Uint8Array;
    export let rawSurveyQuestions: rawSurveyQuestions;

    let page = 0;
    let individualResult: rawQuestionAnswer[] = [];

    async function loadResult() {
        const result =
            await apiClient.survey.controllersSurveySurveyIdResponsesPageGetResponse(
                surveyId,
                page
            );

        for (const answer of decryptAnswers(
            rawPublicKey,
            rawPrivateKey,
            result
        )) {
        }
    }

    onMount(async () => {
        await loadResult();
    });
</script>
