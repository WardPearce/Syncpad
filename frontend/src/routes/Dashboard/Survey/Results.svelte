<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import apiClient from "../../../lib/apiClient";
    import type { SurveyModel } from "../../../lib/client";

    export let surveyId: string;

    let survey: SurveyModel;
    let ws: WebSocket;

    onMount(async () => {
        survey = await apiClient.survey.controllersSurveySurveyIdGetSurvey(
            surveyId
        );

        if (survey.hex_color) await ui("theme", `#${survey.hex_color}`);

        ws = new WebSocket(
            `ws://${apiClient.request.config.BASE.replace(
                "http://",
                ""
            ).replace(
                "http://",
                ""
            )}/controllers/survey/64b891ac33bdfe6a9d418eb6/responses/realtime`
        );

        ws.addEventListener("message", (event) => {
            console.log(JSON.parse(event.data));
        });
    });

    onDestroy(() => {
        ws.close();
    });
</script>
