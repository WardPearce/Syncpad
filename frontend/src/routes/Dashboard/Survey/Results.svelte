<script lang="ts">
    import sodium from "libsodium-wrappers-sumo";
    import { onDestroy, onMount } from "svelte";

    import PageLoading from "../../../components/PageLoading.svelte";
    import Title from "../../../components/Survey/Submit/Title.svelte";
    import apiClient from "../../../lib/apiClient";
    import type { SurveyModel, SurveyResultModel } from "../../../lib/client";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";
    import {
        decryptAnswers,
        decryptSurveyQuestions,
        validateSurvey,
        type RawSurvey,
    } from "../../../lib/survey";

    export let surveyId: string;

    enum ResponseMode {
        individual,
        summary,
    }

    let mode = ResponseMode.summary;

    let survey: SurveyModel;
    let rawSurvey: RawSurvey;
    let rawSurveyQuestions: Record<number, string> = {};

    let summaryResults: Record<number, string[] | Record<string, number>> = {};
    let summaryResultCount: Record<number, number> = {};

    let rawSharedKey: Uint8Array;
    let rawPublicKey: Uint8Array;
    let rawPrivateKey: Uint8Array;
    let rawSignPrivateKey: Uint8Array;
    let rawSignPublicKey: Uint8Array;

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
            )}/controllers/survey/64b891ac33bdfe6a9d418eb6/responses/realtime?pull_history=${pullHistory}`
        );
    }

    function asSummary() {
        summaryResults = {};
        mode = ResponseMode.summary;

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

    async function asIndividual() {
        summaryResults = {};
        mode = ResponseMode.individual;

        if (ws) {
            wsReconnect = false;
            ws.close();
        }

        const result =
            await apiClient.survey.controllersSurveySurveyIdResponsesPageGetResponse(
                surveyId,
                0
            );

        // decryptAnswers(rawPublicKey, rawPrivateKey, result);
    }

    onMount(async () => {
        isLoading = true;

        survey = await apiClient.survey.controllersSurveySurveyIdGetSurvey(
            surveyId
        );

        if (survey.hex_color) await ui("theme", `#${survey.hex_color}`);

        rawSharedKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.secret_key.iv,
            survey.secret_key.cipher_text,
            false
        ) as Uint8Array;
        rawPublicKey = secretKey.decrypt(
            rawSharedKey,
            survey.keypair.public_key.iv,
            survey.keypair.public_key.cipher_text,
            false
        ) as Uint8Array;
        rawPrivateKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.keypair.private_key.iv,
            survey.keypair.private_key.cipher_text,
            false
        ) as Uint8Array;

        rawSignPrivateKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.sign_keypair.iv,
            survey.sign_keypair.cipher_text,
            false
        ) as Uint8Array;
        rawSignPublicKey =
            sodium.crypto_sign_ed25519_sk_to_pk(rawSignPrivateKey);

        validateSurvey(rawSignPublicKey, survey);

        rawSurvey = decryptSurveyQuestions(rawSharedKey, survey);

        rawSurvey.questions.forEach((question) => {
            rawSurveyQuestions[question.id] = question.question;
        });

        if (mode === ResponseMode.individual) {
            await asIndividual();
        } else {
            await asSummary();
        }

        isLoading = false;
    });

    onDestroy(() => {
        if (ws) {
            wsReconnect = false;
            ws.close();
        }
    });
</script>

{#if isLoading}
    <PageLoading />
{:else}
    <div class="center-questions">
        <div class="extra-large-width" style="margin-top: .5em;">
            <nav class="wrap">
                {#if mode === ResponseMode.individual}
                    <button on:click={asSummary}>
                        <i>summarize</i>
                        <span>Summarize responses</span>
                    </button>
                {:else}
                    <button on:click={asIndividual}>
                        <i>call_to_action</i>
                        <span>Individual responses</span>
                    </button>
                {/if}
            </nav>
        </div>

        <Title title={rawSurvey.title} description={rawSurvey.description} />

        {#if mode === ResponseMode.summary}
            {#if Object.keys(summaryResults).length === 0}
                <PageLoading />
            {:else}
                {#each Object.entries(rawSurveyQuestions) as [id, question]}
                    <article class="extra-large-width">
                        <nav>
                            <h5>{question}</h5>
                            <p>({summaryResultCount[id]} responses)</p>
                        </nav>

                        {#if summaryResults[id] instanceof Array}
                            <div
                                style="max-height: 300px;overflow-y: auto;border-radius: 0;"
                            >
                                {#each summaryResults[id] as result}
                                    <div class="row">
                                        <div class="max">{result}</div>
                                        <i>delete</i>
                                    </div>
                                {/each}
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
        {/if}
    </div>
{/if}
