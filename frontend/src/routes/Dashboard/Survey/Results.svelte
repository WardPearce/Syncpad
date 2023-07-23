<script lang="ts">
    import sodium from "libsodium-wrappers-sumo";
    import { onDestroy, onMount } from "svelte";

    import PageLoading from "../../../components/PageLoading.svelte";
    import Title from "../../../components/Survey/Submit/Title.svelte";
    import apiClient from "../../../lib/apiClient";
    import type {
        SurveyModel,
        SurveyQuestionModel,
        SurveyResultModel,
    } from "../../../lib/client";
    import publicKey from "../../../lib/crypto/publicKey";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";
    import {
        decryptSurveyQuestions,
        validateSurvey,
        type RawSurvey,
    } from "../../../lib/survey";

    export let surveyId: string;

    interface RawAnswer {
        id: number;
        type: SurveyQuestionModel.type;
        answer: string | string[];
    }

    let survey: SurveyModel;
    let rawSurvey: RawSurvey;
    let rawAnswers: RawAnswer[][][] = [];

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

    onMount(async () => {
        isLoading = true;

        survey = await apiClient.survey.controllersSurveySurveyIdGetSurvey(
            surveyId
        );

        if (survey.hex_color) await ui("theme", `#${survey.hex_color}`);

        const rawSharedKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.secret_key.iv,
            survey.secret_key.cipher_text,
            false
        ) as Uint8Array;
        const rawPublicKey = secretKey.decrypt(
            rawSharedKey,
            survey.keypair.public_key.iv,
            survey.keypair.public_key.cipher_text,
            false
        ) as Uint8Array;
        const rawPrivateKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.keypair.private_key.iv,
            survey.keypair.private_key.cipher_text,
            false
        ) as Uint8Array;

        const rawSignPrivateKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.sign_keypair.iv,
            survey.sign_keypair.cipher_text,
            false
        ) as Uint8Array;
        const rawSignPublicKey =
            sodium.crypto_sign_ed25519_sk_to_pk(rawSignPrivateKey);

        validateSurvey(rawSignPublicKey, survey);

        rawSurvey = decryptSurveyQuestions(rawSharedKey, survey);

        ws = createWs(true);

        ws.addEventListener("close", () => {
            if (wsReconnect) {
                ws = createWs(false);
            }
        });

        ws.addEventListener("message", (event) => {
            const data = JSON.parse(
                JSON.parse(event.data)
            ) as SurveyResultModel;

            const answers: RawAnswer[] = [];

            data.answers.forEach((answer) => {
                if (answer.answer instanceof Array) {
                    const multipleChoiceAnswers: string[] = [];
                    answer.answer.forEach((answer) => {
                        multipleChoiceAnswers.push(
                            publicKey.boxSealOpen(
                                rawPublicKey,
                                rawPrivateKey,
                                answer,
                                true
                            ) as string
                        );
                    });

                    answers.push({
                        id: answer.id,
                        type: answer.type,
                        answer: multipleChoiceAnswers,
                    });
                } else {
                    answers.push({
                        id: answer.id,
                        type: answer.type,
                        answer: publicKey.boxSealOpen(
                            rawPublicKey,
                            rawPrivateKey,
                            answer.answer,
                            true
                        ) as string,
                    });
                }
            });

            rawAnswers.push([answers]);
        });

        isLoading = false;
    });

    onDestroy(() => {
        wsReconnect = false;
        ws.close();
    });
</script>

{#if isLoading}
    <PageLoading />
{:else}
    <div class="center-questions">
        <Title title={rawSurvey.title} description={rawSurvey.description} />
    </div>
{/if}
