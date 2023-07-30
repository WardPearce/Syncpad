<script lang="ts">
    import { onDestroy, onMount } from "svelte";

    import apiClient from "../../../lib/apiClient";
    import type { SurveyResultModel } from "../../../lib/client";
    import { decryptAnswers, type RawSurvey } from "../../../lib/survey";
    import PageLoading from "../../PageLoading.svelte";

    export let surveyId: string;
    export let rawPublicKey: Uint8Array;
    export let rawPrivateKey: Uint8Array;
    export let rawSurvey: RawSurvey;
    export let rawSurveyQuestions: Record<number, string> = {};

    let summaryResults: Record<number, string[] | Record<string, number>> = {};
    let summaryResultCount: Record<number, number> = {};

    let isLoading = true;

    let ws: WebSocket;
    let wsReconnect = true;

    function createWs(pullHistory: boolean): WebSocket {
        return new WebSocket(
            `ws://${apiClient.request.config.BASE.replace(
                "http://",
                ""
            ).replace(
                "https://",
                ""
            )}/controllers/survey/${surveyId}/responses/realtime?pull_history=${pullHistory}`
        );
    }

    function asSummary() {
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
                    surveyChoices[question.id][choice.id.toString()] =
                        choice.choice;
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

                        const choice = surveyChoices[answer.id][selectedChoice];

                        if (!(choice in summaryResults[answer.id])) {
                            summaryResults[answer.id][choice] = 0;
                        }

                        summaryResults[answer.id][choice]++;
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
                        summaryResults[answer.id][choice] = 0;
                    }

                    summaryResults[answer.id][choice]++;
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
    }

    onMount(async () => {
        isLoading = true;

        await asSummary();

        isLoading = false;
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
    {#each Object.entries(rawSurveyQuestions) as [id, question]}
        <article class="extra-large-width">
            <nav>
                <h5>{question}</h5>
                {#if id in summaryResultCount}
                    <p>({summaryResultCount[id]} responses)</p>
                {:else}
                    <p>(No responses)</p>
                {/if}
            </nav>

            {#if summaryResults[id] instanceof Array}
                <div
                    style="max-height: 350px;overflow-y: auto;border-radius: 0;"
                >
                    <ul>
                        {#each summaryResults[id] as result}
                            <li style="margin-top: 1em;">
                                <article class="surface-variant">
                                    <p>{result}</p>
                                </article>
                            </li>
                        {/each}
                    </ul>
                </div>
            {:else if summaryResults[id] instanceof Object}
                <div class="grid">
                    {#each Object.entries(summaryResults[id]) as [choice, result]}
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
