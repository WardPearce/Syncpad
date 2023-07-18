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
    import type { SurveyAnswerModel, SurveyPublicModel } from "../lib/client";
    import { base64Decode } from "../lib/crypto/codecUtils";
    import hash from "../lib/crypto/hash";
    import publicKey from "../lib/crypto/publicKey";
    import secretKey from "../lib/crypto/secretKey";
    import signatures from "../lib/crypto/signatures";
    import { localSecrets } from "../stores";

    interface rawQuestionAnswer extends rawQuestion {
        answer: number | number[] | string | null;
        error: string | null;
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
    let errorMsg = "";
    let submissionError = false;

    onMount(async () => {
        surveyLoading = true;

        try {
            survey =
                await apiClient.survey.controllersSurveySurveyIdPublicPublicSurvey(
                    surveyId
                );
        } catch (error) {
            errorMsg = error.body.detail;
            surveyLoading = false;
            return;
        }

        let rawKey: Uint8Array;
        try {
            rawKey = base64Decode(b64EncodedRawKey, true);
        } catch {
            errorMsg = "Invalid key format";
            surveyLoading = false;
            return;
        }

        try {
            rawSignPublicKey = base64Decode(survey.sign_keypair.public_key);
        } catch {
            errorMsg = "Invalid sign public key hash format";
            surveyLoading = false;
            return;
        }

        try {
            rawPublicKey = secretKey.decrypt(
                rawKey,
                survey.keypair.public_key.iv,
                survey.keypair.public_key.cipher_text
            ) as Uint8Array;
        } catch {
            errorMsg = "Invalid key";
            surveyLoading = false;
            return;
        }

        if (
            hash.hashBase64Encode(rawSignPublicKey, true) !== signPublicKeyHash
        ) {
            errorMsg =
                "Public key hash does not match what the server provided, please make sure you inputted the url correctly.";
            surveyLoading = false;
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
        } catch {
            errorMsg = "Failed to validate survey signature";
            surveyLoading = false;
            return;
        }

        if (survey.hex_color) await ui("theme", `#${survey.hex_color}`);

        try {
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
                    error: null,
                });
            });
        } catch {
            errorMsg = "Failed to decrypt survey";
            surveyLoading = false;
            return;
        }

        surveyLoading = false;
    });

    async function submit() {
        const encryptedAnswers: SurveyAnswerModel[] = [];
        submissionError = false;

        rawQuestions.forEach((question) => {
            if (!question.answer) {
                if (question.required) {
                    question.error = "This question is required";
                    submissionError = true;
                    return;
                }
                return;
            }

            if (
                question.regex &&
                typeof question.answer === "string" &&
                safe(question.regex)
            ) {
                const regex = new RegExp(question.regex);
                if (!regex.test(question.answer)) {
                    question.error = "Regex does not match";
                    submissionError = true;
                    return;
                }
            }

            let answer: string[] | string;
            if (question.answer instanceof Array) {
                answer = [];
                question.answer.forEach((choiceId) => {
                    (answer as string[]).push(
                        publicKey.boxSeal(rawPublicKey, choiceId.toString())
                    );
                });
            } else {
                answer = publicKey.boxSeal(
                    rawPublicKey,
                    question.answer.toString()
                );
            }

            question.error = null;

            encryptedAnswers.push({
                id: question.id,
                type: question.type,
                answer: answer,
            });
        });

        if (submissionError) {
            rawQuestions = [...rawQuestions];
            return;
        }

        await apiClient.survey.controllersSurveySurveyIdSubmitSubmitSurvey(
            surveyId,
            {
                answers: encryptedAnswers,
            }
        );
    }

    async function determineSubmitPrompt() {
        if (survey.proxy_block || !survey.allow_multiple_submissions)
            showSubmitDialog = true;
        else await submit();
    }
</script>

{#if surveyLoading}
    <PageLoading />
{:else if survey.requires_login && get(localSecrets) === null}
    <h4>This survey requires an account</h4>
    <p>Please login or register to continue.</p>
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
{:else if errorMsg}
    <h4>Failed to load survey</h4>
    <p>{errorMsg}</p>
{:else}
    <dialog class:active={showSubmitDialog} class="large-width">
        <h5>Important privacy note</h5>
        {#if survey.proxy_block}
            <p>
                This survey processes your IP on submission to ensure you aren't
                using a proxy or VPN regardless of your account IP processing
                preference. {#if survey.allow_multiple_submissions}Your IP is
                    not stored after processing by {import.meta.env
                        .VITE_SITE_NAME}{/if}. Please contact the survey owner
                if you wish to disable this.
            </p>
        {/if}
        {#if !survey.allow_multiple_submissions}
            <p>
                This survey only allows one submission per account. A salted
                hash of your IP address will be stored in {import.meta.env
                    .VITE_SITE_NAME} for 24 hours to ensure you can't submit the
                survey again. Please contact the survey owner if you wish to disable
                this.
            </p>
        {/if}
        <nav class="right-align">
            <button on:click={() => (showSubmitDialog = false)} class="border"
                >Cancel</button
            >
            <button on:click={submit}>Yes I'd like to continue</button>
        </nav>
    </dialog>

    <div class="center-questions">
        <div class="extra-large-width">
            <nav class="right-align wrap">
                <div class="chip surface-variant small">
                    <i class="primary-text">security</i>
                    <div class="tooltip bottom">
                        This survey is end-to-end encrypted.
                    </div>
                </div>
                <div class="chip surface-variant small">
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
                <div class="chip surface-variant small">
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
                <div class="chip surface-variant small">
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
                <div class="chip surface-variant small">
                    <i class:primary-text={survey.requires_captcha}>smart_toy</i
                    >
                    <div class="tooltip bottom">
                        Captcha is
                        {#if !survey.requires_captcha}
                            not
                        {/if}
                        required
                    </div>
                </div>
            </nav>

            <nav class="right-align">
                <button on:click={determineSubmitPrompt}>Complete survey</button
                >
            </nav>
        </div>

        {#if submissionError}
            <div class="extra-large-width" style="margin-top: 1em;">
                <article class="error middle-align">
                    <i>error</i>
                    <span>There was an error with your submission.</span>
                </article>
            </div>
        {/if}

        <Title title={rawTitle} description={rawDescription} />

        {#each rawQuestions as question}
            <Question {...question} bind:answer={question.answer} />
        {/each}

        <div class="extra-large-width" style="margin-top: 1em;">
            <nav class="right-align">
                <button on:click={determineSubmitPrompt}>Complete survey</button
                >
            </nav>
        </div>
    </div>
{/if}
