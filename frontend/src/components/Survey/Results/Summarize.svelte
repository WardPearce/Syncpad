<script lang="ts">
    import { onDestroy, onMount } from "svelte";

    import apiClient from "../../../lib/apiClient";
    import type { SurveyResultModel } from "../../../lib/client";
    import { decryptAnswers, type rawSurvey } from "../../../lib/survey";
    import PageLoading from "../../PageLoading.svelte";
    import type { rawSurveyQuestions } from "../types";

    export let surveyId: string;
    export let rawPublicKey: Uint8Array;
    export let rawPrivateKey: Uint8Array;
    export let rawSurvey: rawSurvey;
    export let rawSurveyQuestions: rawSurveyQuestions;

    let summaryResults: Record<number, string[] | Record<string, number>> = {};
    let summaryResultCount: Record<number, number> = {};

    let ws: WebSocket;
    let wsReconnect = true;

    function createWs(pullHistory: boolean): WebSocket {
        return new WebSocket(
            `wss://${apiClient.request.config.BASE.replace(
                "http://",
                ""
            ).replace(
                "https://",
                ""
            )}/controllers/survey/responses/realtime/${surveyId}/?pull_history=${pullHistory}`
        );
    }

    onMount(async () => {
        summaryResults = {};

        ws = createWs(true);

        ws.onclose = () => {
            if (wsReconnect) {
                ws = createWs(true);
            }
        };

        const surveyChoices: Record<number, Record<number, string>> = {};
        rawSurvey.questions.forEach((question) => {
            if (question.choices.length > 0) {
                if (!(question.id in surveyChoices))
                    surveyChoices[question.id] = {};

                question.choices.forEach((choice) => {
                    surveyChoices[question.id][choice.id] = choice.choice;
                });
            }
        });

        ws.onmessage = (event: MessageEvent<any>) => {
            const data = JSON.parse(
                JSON.parse(event.data)
            ) as SurveyResultModel;

            for (const answer of decryptAnswers(
                rawPublicKey,
                rawPrivateKey,
                data
            )) {
                if (answer.answer instanceof Array) {
                    if (!(answer.id in summaryResults)) {
                        summaryResults[answer.id] = {};
                        summaryResultCount[answer.id] = 0;
                    }

                    summaryResultCount[answer.id]++;

                    answer.answer.forEach((selectedChoice) => {
                        if (!(selectedChoice in surveyChoices[answer.id])) {
                            return;
                        }

                        const choice =
                            surveyChoices[answer.id][Number(selectedChoice)];

                        if (!(choice in summaryResults[answer.id])) {
                            (
                                summaryResults[answer.id] as Record<
                                    string,
                                    number
                                >
                            )[choice] = 0;
                        }

                        (summaryResults[answer.id] as Record<string, number>)[
                            choice
                        ]++;
                    });
                } else if (answer.type === 3) {
                    if (!(answer.id in summaryResults)) {
                        summaryResults[answer.id] = {};
                        summaryResultCount[answer.id] = 0;
                    }

                    summaryResultCount[answer.id]++;

                    const choice =
                        surveyChoices[answer.id][Number(answer.answer)];

                    if (!(choice in summaryResults[answer.id])) {
                        (summaryResults[answer.id] as Record<string, number>)[
                            choice
                        ] = 0;
                    }

                    (summaryResults[answer.id] as Record<string, number>)[
                        choice
                    ]++;
                } else {
                    if (!(answer.id in summaryResults)) {
                        summaryResults[answer.id] = [];
                        summaryResultCount[answer.id] = 0;
                    }

                    summaryResultCount[answer.id]++;

                    (summaryResults[answer.id] as string[]).push(answer.answer);
                }

                summaryResults = { ...summaryResults };
                summaryResultCount = { ...summaryResultCount };
            }
        };
    });

    onDestroy(() => {
        if (ws) {
            wsReconnect = false;
            ws.close();
        }
    });
</script>

{#if Object.keys(summaryResults).length === 0}
    <PageLoading />
{:else}
    {#each Object.entries(rawSurveyQuestions) as [id, details]}
        <article class="extra-large-width">
            <h5>
                {details.question}
                <span style="font-size: .5em; margin-left: 1em;">
                    {#if id in summaryResultCount}
                        ({summaryResultCount[Number(id)]} responses)
                    {:else}
                        (No responses)
                    {/if}
                </span>
            </h5>
            {#if details.description}
                <p>{details.description}</p>
            {/if}

            {#if summaryResults[Number(id)] instanceof Array}
                <div
                    style="max-height: 350px;overflow-y: auto;border-radius: 0;"
                >
                    <ul>
                        {#each Object.values(summaryResults[Number(id)]) as result}
                            <li style="margin-top: 1em;">
                                <article class="surface-variant">
                                    <p>{result}</p>
                                </article>
                            </li>
                        {/each}
                    </ul>
                </div>
            {:else if summaryResults[Number(id)] instanceof Object}
                <div class="grid">
                    {#each Object.entries(summaryResults[Number(id)]) as [choice, result]}
                        <div class="s12 m6 l4">
                            <article class="surface-variant">
                                <h6>{choice}</h6>
                                <p style="font-size: 2em;">
                                    {result}
                                </p>
                            </article>
                        </div>
                    {/each}
                </div>
            {/if}
        </article>
    {/each}
{/if}
