<script lang="ts">
    import sodium from "libsodium-wrappers-sumo";
    import { onDestroy, onMount } from "svelte";

    import PageLoading from "../../../components/PageLoading.svelte";
    import Summarize from "../../../components/Survey/Results/Summarize.svelte";
    import Title from "../../../components/Survey/Submit/Title.svelte";
    import apiClient from "../../../lib/apiClient";
    import type { SurveyModel } from "../../../lib/client";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";
    import {
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
            )}/controllers/survey/${surveyId}/responses/realtime?pull_history=${pullHistory}`
        );
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
                    <button on:click={() => (mode = ResponseMode.summary)}>
                        <i>summarize</i>
                        <span>Summarize responses</span>
                    </button>
                {:else}
                    <button on:click={() => (mode = ResponseMode.individual)}>
                        <i>call_to_action</i>
                        <span>Individual responses</span>
                    </button>
                {/if}
            </nav>
        </div>

        <Title title={rawSurvey.title} description={rawSurvey.description} />

        {#if mode === ResponseMode.summary}
            <Summarize
                {surveyId}
                {rawSurvey}
                {rawSurveyQuestions}
                {rawPrivateKey}
                {rawPublicKey}
            />
        {/if}
    </div>
{/if}
