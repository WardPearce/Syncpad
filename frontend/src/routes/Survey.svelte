<script lang="ts">
    import safe from "safe-regex";
    import { onMount } from "svelte";
    import { navigate, useLocation } from "svelte-navigator";
    import { get } from "svelte/store";
    import PageLoading from "../components/PageLoading.svelte";
    import Question from "../components/Survey/Submit/Question.svelte";
    import Title from "../components/Survey/Submit/Title.svelte";
    import { normalizeSurveyQuestions } from "../components/Survey/helpers";
    import {
        type rawChoice,
        type rawQuestion,
    } from "../components/Survey/types";
    import apiClient from "../lib/apiClient";
    import type { SurveyPublicModel, SurveyQuestionModel } from "../lib/client";
    import { base64Decode } from "../lib/crypto/codecUtils";
    import hash from "../lib/crypto/hash";
    import publicKey from "../lib/crypto/publicKey";
    import secretKey from "../lib/crypto/secretKey";
    import signatures from "../lib/crypto/signatures";
    import { localSecrets } from "../stores";

    interface rawQuestionAnswer extends rawQuestion {
        answer: number | number[] | string | null;
    }

    export let surveyId: string;
    export let signPublicKeyHash: string;

    const b64EncodedRawKey: string = location.hash.substring(1);

    let surveyLoading = true;

    let survey: SurveyPublicModel;

    let rawTitle: string;
    let rawDescription: string | undefined;
    let rawQuestions: rawQuestionAnswer[] = [];
    let rawPublicKey: Uint8Array;
    let rawSignPublicKey: Uint8Array;

    let showSubmitDialog = false;

    onMount(async () => {
        surveyLoading = true;

        survey =
            await apiClient.survey.controllersSurveySurveyIdPublicPublicSurvey(
                surveyId
            );

        const rawKey = base64Decode(b64EncodedRawKey, true);

        rawSignPublicKey = base64Decode(survey.sign_keypair.public_key);
        rawPublicKey = secretKey.decrypt(
            rawKey,
            survey.keypair.public_key.iv,
            survey.keypair.public_key.cipher_text
        ) as Uint8Array;

        if (
            hash.hashBase64Encode(rawSignPublicKey, true) !== signPublicKeyHash
        ) {
            return;
        }

        const toValidate: Record<string, any> = {
            title: {
                cipher_text: survey.title.cipher_text,
                iv: survey.title.iv,
            },
            questions: normalizeSurveyQuestions(survey.questions),
            keypair: {
                public_key: {
                    cipher_text: survey.keypair.public_key.cipher_text,
                    iv: survey.keypair.public_key.iv,
                },
            },
        };

        if (survey.description) {
            toValidate.description = {
                cipher_text: survey.description.cipher_text,
                iv: survey.description.iv,
            };
        }

        try {
            signatures.validateHash(
                rawSignPublicKey,
                survey.signature,
                JSON.stringify(toValidate)
            );
        } catch (error) {
            return;
        }

        rawTitle = secretKey.decrypt(
            rawKey,
            survey.title.iv,
            survey.title.cipher_text,
            true
        ) as string;

        if (survey.description)
            rawDescription = secretKey.decrypt(
                rawKey,
                survey.description.iv,
                survey.description.cipher_text,
                true
            ) as string;

        survey.questions.forEach((question) => {
            let choices: rawChoice[] = [];
            if (question.choices)
                question.choices.forEach((choice) => {
                    choices.push({
                        id: choice.id,
                        choice: secretKey.decrypt(
                            rawKey,
                            choice.iv,
                            choice.cipher_text,
                            true
                        ) as string,
                    });
                });

            let rawRegex: string | null = null;
            if (question.regex) {
                rawRegex = secretKey.decrypt(
                    rawKey,
                    question.regex.iv,
                    question.regex.cipher_text,
                    true
                ) as string;

                // If regex not demeed safe, set to null
                // Not prefect, but worse case someone
                // freezes someones browser
                if (!safe(rawRegex)) rawRegex = null;
            }

            rawQuestions.push({
                answer: null,
                id: question.id,
                question: secretKey.decrypt(
                    rawKey,
                    question.question.iv,
                    question.question.cipher_text,
                    true
                ) as string,
                description: question.description
                    ? (secretKey.decrypt(
                          rawKey,
                          question.description.iv,
                          question.description.cipher_text,
                          true
                      ) as string)
                    : null,
                required: question.required as boolean,
                type: question.type,
                choices: choices,
                regex: rawRegex,
            });
        });

        surveyLoading = false;
    });

    async function submit() {
        const encryptedAnswers: {
            id: number;
            answer: string[];
            type: SurveyQuestionModel.type;
        }[] = [];

        rawQuestions.forEach((question) => {
            if (!question.answer) return;

            let answer: string[] = [];
            if (question.answer instanceof Array) {
                question.answer.forEach((choiceId) => {
                    answer.push(
                        publicKey.boxSeal(rawPublicKey, choiceId.toString())
                    );
                });
            } else {
                answer = [
                    publicKey.boxSeal(rawPublicKey, question.answer.toString()),
                ];
            }

            encryptedAnswers.push({
                id: question.id,
                type: question.type,
                answer: answer,
            });
        });
    }

    async function determineSubmitPrompt() {
        if (survey.proxy_block) showSubmitDialog = true;
        else await submit();
    }
</script>

{#if surveyLoading}
    <PageLoading />
{:else if survey.requires_login && get(localSecrets) === null}
    <h4>This survey requires an account</h4>
    <p>
        This survey requires an account to ensure that you can only submit once.
        Please login or register to continue.
    </p>
    <nav>
        <button
            class="large"
            on:click={() =>
                navigate("/login", {
                    state: { redirect: get(useLocation()).pathname },
                })}>Login</button
        >
        <button
            class="large border"
            on:click={() =>
                navigate("/register", {
                    state: { redirect: get(useLocation()).pathname },
                })}>Register</button
        >
    </nav>
{:else}
    <dialog class:active={showSubmitDialog} class="large-width">
        <h5>Important privacy note</h5>
        <p>
            This survey processes your IP on submission to ensure you aren't
            using a proxy or VPN regardless of your account IP processing
            preference. Your IP is not stored after processing by {import.meta
                .env.VITE_SITE_NAME}. Please contact the survey owner if you
            wish to disable this.
        </p>
        <nav class="right-align">
            <button on:click={() => (showSubmitDialog = false)} class="border"
                >Cancel</button
            >
            <button on:click={submit}>Yes I'd like to continue</button>
        </nav>
    </dialog>

    <div class="center-questions">
        <article class="extra-large-width secondary-container">
            <h6 style="margin-bottom: 0;">End-to-end encrypted</h6>

            <nav style="margin: 0;">
                <div>
                    <i class:primary-text={survey.requires_login}
                        >account_circle</i
                    >
                    <div class="tooltip bottom">
                        Login is
                        {#if !survey.requires_login}
                            not
                        {/if}
                        required
                    </div>
                </div>
                <div>
                    <i class:primary-text={survey.proxy_block}>travel_explore</i
                    >
                    <div class="tooltip bottom">
                        Proxy/VPN blocking is
                        {#if !survey.proxy_block}
                            not
                        {/if}
                        enabled
                    </div>
                </div>
                <div>
                    <i class:primary-text={survey.allow_multiple_submissions}
                        >dynamic_feed</i
                    >
                    <div class="tooltip bottom">
                        Multiple submissions are
                        {#if !survey.allow_multiple_submissions}
                            not
                        {/if}
                        allowed
                    </div>
                </div>
            </nav>

            <p>
                All answers are encrypted on your device before being sent to
                the server. Only you and the survey creator can see your
                answers.
            </p>

            <nav class="right-align">
                <button on:click={determineSubmitPrompt}>Complete survey</button
                >
            </nav>
        </article>

        <Title title={rawTitle} description={rawDescription} />

        {#each rawQuestions as question}
            <Question {...question} bind:answer={question.answer} />
        {/each}

        <button style="margin-top: 2em;" on:click={determineSubmitPrompt}
            >Complete survey</button
        >
    </div>
{/if}
