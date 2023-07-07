<script lang="ts">
    import { onMount } from "svelte";
    import apiClient from "../lib/apiClient";

    export let surveyId: string;
    export let publicKeyHash: string;
    export let SignPublicKeyHash: string;

    onMount(async () => {
        await apiClient.survey.controllersSurveySurveyIdPublicPublicSurvey(
            surveyId
        );
    });
</script>
