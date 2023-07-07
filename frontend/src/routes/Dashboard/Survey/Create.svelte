<script lang="ts">
    import { dndzone } from "svelte-dnd-action";

    import { navigate } from "svelte-navigator";
    import PageLoading from "../../../components/PageLoading.svelte";
    import Question from "../../../components/Survey/Create/Question.svelte";
    import Title from "../../../components/Survey/Create/Title.svelte";
    import {
        SurveyAnswerType,
        type rawQuestion,
    } from "../../../components/Survey/types";
    import apiClient from "../../../lib/apiClient";
    import type {
        SurveyCreateModel,
        SurveyQuestionModel,
    } from "../../../lib/client";
    import { base64Encode } from "../../../lib/crypto/codecUtils";
    import hash from "../../../lib/crypto/hash";
    import publicKey from "../../../lib/crypto/publicKey";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";
    import signatures from "../../../lib/crypto/signatures";

    let lastQuestionIdId = 0;
    let surveyTitle = "Untitled survey";
    let surveyDescription = "";
    let surveyQuestions: rawQuestion[] = [];
    let dragDisabled = true;
    let publishingSurvey = false;

    addQuestion();

    function startDrag() {
        dragDisabled = false;
    }

    function stopDrag() {
        dragDisabled = true;
    }

    function handleConsider(event) {
        surveyQuestions = event.detail.items;
    }

    function handleFinalize(event) {
        surveyQuestions = event.detail.items;
        dragDisabled = true;
    }

    function addQuestion() {
        surveyQuestions = [
            ...surveyQuestions,
            {
                id: lastQuestionIdId++,
                regex: null,
                required: false,
                question: "Untitled Question",
                type: SurveyAnswerType["Short Answer"],
                description: null,
                choices: [],
            },
        ];
    }

    function duplicateQuestion(index: number) {
        const question = surveyQuestions.find(
            (question) => question.id === index
        );
        if (question) {
            surveyQuestions = [
                ...surveyQuestions,
                {
                    id: lastQuestionIdId++,
                    regex: question.regex,
                    required: question.required,
                    question: question.question,
                    type: question.type,
                    description: question.description,
                    choices: question.choices,
                },
            ];
        }
    }

    function removeQuestion(index: number) {
        surveyQuestions = surveyQuestions.filter(
            (question) => question.id !== index
        );
    }

    async function onPublish() {
        publishingSurvey = true;

        const rawKey = secretKey.generateKey();
        const rawKeyPair = publicKey.generateKeypair();
        const rawSignKeyPair = signatures.generateKeypair();

        let questionsEncrypted: SurveyQuestionModel[] = [];

        for (const question of surveyQuestions) {
            const questionEncrypted = secretKey.encrypt(
                rawKey,
                question.question
            );
            const regexEncrypted = question.regex
                ? secretKey.encrypt(rawKey, question.regex)
                : null;
            const descriptionEncrypted = question.description
                ? secretKey.encrypt(rawKey, question.description)
                : null;

            const payload: SurveyQuestionModel = {
                id: question.id,
                regex: regexEncrypted
                    ? {
                          cipher_text: regexEncrypted.cipherText,
                          iv: regexEncrypted.iv,
                      }
                    : null,
                description: descriptionEncrypted
                    ? {
                          cipher_text: descriptionEncrypted.cipherText,
                          iv: descriptionEncrypted.iv,
                      }
                    : null,
                required: question.required,
                question: {
                    cipher_text: questionEncrypted.cipherText,
                    iv: questionEncrypted.iv,
                },
                type: question.type,
            };

            if (question.choices && question.choices.length > 0) {
                payload.choices = [];

                for (const choice of question.choices) {
                    const choiceEncrypted = secretKey.encrypt(rawKey, choice);
                    payload.choices.push({
                        cipher_text: choiceEncrypted.cipherText,
                        iv: choiceEncrypted.iv,
                    });
                }
            }

            questionsEncrypted.push(payload);
        }

        const surveyTitleEncrypted = secretKey.encrypt(rawKey, surveyTitle);
        const surveyDescriptionEncrypted = secretKey.encrypt(
            rawKey,
            surveyDescription
        );
        const publicKeypairEncrypted = secretKey.encrypt(
            rawKey,
            rawKeyPair.publicKey
        );

        const signKeypairEncrypted = secretKey.encrypt(
            SecretkeyLocation.localKeychain,
            rawSignKeyPair.privateKey
        );
        const privateKeypairEncrypted = secretKey.encrypt(
            SecretkeyLocation.localKeychain,
            rawKeyPair.privateKey
        );
        const secretKeyEncrypted = secretKey.encrypt(
            SecretkeyLocation.localKeychain,
            rawKey
        );

        const surveyPayload: SurveyCreateModel = {
            title: {
                cipher_text: surveyTitleEncrypted.cipherText,
                iv: surveyTitleEncrypted.iv,
            },
            description: {
                cipher_text: surveyDescriptionEncrypted.cipherText,
                iv: surveyDescriptionEncrypted.iv,
            },
            questions: questionsEncrypted,
            secret_key: {
                cipher_text: secretKeyEncrypted.cipherText,
                iv: secretKeyEncrypted.iv,
            },
            sign_keypair: {
                cipher_text: signKeypairEncrypted.cipherText,
                iv: signKeypairEncrypted.iv,
                public_key: base64Encode(rawSignKeyPair.publicKey),
            },
            keypair: {
                private_key: {
                    cipher_text: privateKeypairEncrypted.cipherText,
                    iv: privateKeypairEncrypted.iv,
                },
                public_key: {
                    cipher_text: publicKeypairEncrypted.cipherText,
                    iv: publicKeypairEncrypted.iv,
                },
            },
            signature: "",
        };

        surveyPayload.signature = signatures.signHash(
            rawSignKeyPair.privateKey,
            JSON.stringify(surveyPayload)
        );

        const savedSurvey =
            await apiClient.survey.controllersSurveyCreateCreateSurvey(
                surveyPayload
            );

        navigate(
            `/s/${savedSurvey._id}/${hash.hashBase64Encode(
                rawKeyPair.publicKey,
                true
            )}/${hash.hashBase64Encode(
                rawSignKeyPair.publicKey,
                true
            )}#${base64Encode(rawKey, true)}`,
            {
                replace: true,
            }
        );

        publishingSurvey = false;
    }
</script>

{#if publishingSurvey}
    <PageLoading />
{:else}
    <div class="center-questions">
        <article class="extra-large-width secondary-container">
            <h6>Ensuring Secure and Confidential Survey Data</h6>

            <p>
                All survey questions, answers, and sensitive metadata are
                protected through end-to-end encryption. This means that only
                the individuals who you share the link with can view the
                questions, while the answers remain confidential and accessible
                only to you.
            </p>

            <nav class="right-align">
                <button on:click={onPublish}>
                    <i>publish</i>
                    <span>Publish</span>
                </button>
            </nav>
        </article>
        <Title title={surveyTitle} description={surveyDescription} />

        <div
            use:dndzone={{
                items: surveyQuestions,
                dragDisabled: dragDisabled,
                morphDisabled: true,
                dropTargetClasses: ["drop-target"],
            }}
            on:consider={handleConsider}
            on:finalize={handleFinalize}
            style="margin-top: 1em;"
        >
            {#each surveyQuestions as question (question.id)}
                <Question
                    questionId={question.id}
                    bind:regex={question.regex}
                    bind:description={question.description}
                    bind:required={question.required}
                    bind:question={question.question}
                    bind:type={question.type}
                    bind:choices={question.choices}
                    {duplicateQuestion}
                    {removeQuestion}
                    {startDrag}
                    {stopDrag}
                />
            {/each}
        </div>

        <button on:click={addQuestion} style="margin-top: 2em;">
            <i>add</i>
            <span>New Question</span>
        </button>
    </div>
{/if}

<style>
    .center-questions {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>
