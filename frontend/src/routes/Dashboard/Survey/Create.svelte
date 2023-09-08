<script lang="ts">
    import sodium from "libsodium-wrappers-sumo";
    import safe from "safe-regex";
    import { dndzone } from "svelte-dnd-action";

    import { navigate } from "svelte-navigator";
    import PageLoading from "../../../components/PageLoading.svelte";
    import Question from "../../../components/Survey/Create/Question.svelte";
    import Title from "../../../components/Survey/Create/Title.svelte";
    import { type rawQuestion } from "../../../components/Survey/types";
    import apiClient from "../../../lib/apiClient";
    import {
        SurveyQuestionModel,
        type SurveyCreateModel,
    } from "../../../lib/client";
    import { base64Encode } from "../../../lib/crypto/codecUtils";
    import hash from "../../../lib/crypto/hash";
    import publicKey from "../../../lib/crypto/publicKey";
    import secretKey, {
        SecretkeyLocation,
        type encryptedData,
    } from "../../../lib/crypto/secretKey";
    import signatures from "../../../lib/crypto/signatures";
    import { localToUtc } from "../../../lib/date";
    import { normalizeSurveyQuestions } from "../../../lib/survey";

    let lastQuestionIdId = 0;
    let surveyTitle = "Untitled survey";
    let surveyDescription = "";
    let surveyQuestions: rawQuestion[] = [];
    let dragDisabled = true;
    let publishingSurvey = false;
    let requireAccount = false;
    let proxyBlock = false;
    let allowMultipleSubmissions = true;
    let requireCaptcha = false;
    let surveyCloses: Date | null = null;
    let surveyTheme = import.meta.env.VITE_THEME;

    addQuestion();

    async function previewTheme() {
        await ui("theme", surveyTheme);
    }

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
                type: SurveyQuestionModel.type._0,
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
            let regexEncrypted: encryptedData | null = null;
            if (question.regex) {
                if (!safe(question.regex)) {
                    return;
                }

                regexEncrypted = secretKey.encrypt(rawKey, question.regex);
            }

            const questionEncrypted = secretKey.encrypt(
                rawKey,
                question.question
            );
            const descriptionEncrypted = question.description
                ? secretKey.encrypt(rawKey, question.description)
                : null;

            const payload: SurveyQuestionModel = {
                choices: null,
                id: question.id,
                regex: regexEncrypted
                    ? {
                          iv: regexEncrypted.iv,
                          cipher_text: regexEncrypted.cipherText,
                      }
                    : null,
                description: descriptionEncrypted
                    ? {
                          iv: descriptionEncrypted.iv,
                          cipher_text: descriptionEncrypted.cipherText,
                      }
                    : null,
                required: question.required,
                question: {
                    iv: questionEncrypted.iv,
                    cipher_text: questionEncrypted.cipherText,
                },
                type: question.type,
            };

            if (question.choices && question.choices.length > 0) {
                payload.choices = [];

                for (const choice of question.choices) {
                    const choiceEncrypted = secretKey.encrypt(
                        rawKey,
                        choice.choice
                    );
                    payload.choices.push({
                        id: choice.id,
                        iv: choiceEncrypted.iv,
                        cipher_text: choiceEncrypted.cipherText,
                    });
                }
            }

            questionsEncrypted.push(payload);
        }

        const surveyTitleEncrypted = secretKey.encrypt(rawKey, surveyTitle);
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
        const signPublicKeyEncoded = base64Encode(rawSignKeyPair.publicKey);

        const surveyPayload: SurveyCreateModel = {
            title: {
                cipher_text: surveyTitleEncrypted.cipherText,
                iv: surveyTitleEncrypted.iv,
            },
            questions: questionsEncrypted,
            secret_key: {
                cipher_text: secretKeyEncrypted.cipherText,
                iv: secretKeyEncrypted.iv,
            },
            sign_keypair: {
                cipher_text: signKeypairEncrypted.cipherText,
                iv: signKeypairEncrypted.iv,
                public_key: signPublicKeyEncoded,
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
            allow_multiple_submissions: allowMultipleSubmissions,
            proxy_block: proxyBlock,
            requires_login: requireAccount,
            requires_captcha: requireCaptcha,
            hex_color: surveyTheme.replace("#", ""),
            closed: surveyCloses
                ? localToUtc(surveyCloses).format()
                : undefined,
            signature: "",
        };

        const toSign: Record<string, any> = {
            title: {
                cipher_text: surveyTitleEncrypted.cipherText,
                iv: surveyTitleEncrypted.iv,
            },
            questions: normalizeSurveyQuestions(questionsEncrypted),
            keypair: {
                public_key: {
                    cipher_text: publicKeypairEncrypted.cipherText,
                    iv: publicKeypairEncrypted.iv,
                },
            },
        };

        if (surveyDescription) {
            const surveyDescriptionEncrypted = secretKey.encrypt(
                rawKey,
                surveyDescription
            );
            surveyPayload.description = {
                cipher_text: surveyDescriptionEncrypted.cipherText,
                iv: surveyDescriptionEncrypted.iv,
            };
            toSign.description = {
                cipher_text: surveyDescriptionEncrypted.cipherText,
                iv: surveyDescriptionEncrypted.iv,
            };
        }

        if (!allowMultipleSubmissions) {
            const ipHmacKey = sodium.randombytes_buf(32);
            const ipHmacKeyEncrypted = secretKey.encrypt(rawKey, ipHmacKey);

            // Raw ipHmacKey sent what is then hashed by the server and
            // discarded.
            surveyPayload.ip = {
                key: base64Encode(ipHmacKey, false),
                cipher_text: ipHmacKeyEncrypted.cipherText,
                iv: ipHmacKeyEncrypted.iv,
            };

            toSign.ip = {
                cipher_text: ipHmacKeyEncrypted.cipherText,
                iv: ipHmacKeyEncrypted.iv,
            };
        }

        surveyPayload.signature = signatures.signHash(
            rawSignKeyPair.privateKey,
            JSON.stringify(toSign)
        );

        const savedSurvey =
            await apiClient.survey.controllersSurveyCreateCreateSurvey(
                surveyPayload
            );

        navigate(
            `/s/${savedSurvey._id}/${hash.hashBase64Encode(
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
            <ul>
                <li>
                    <label class="checkbox">
                        <input type="checkbox" bind:checked={requireAccount} />
                        <span>Require account</span>
                    </label>
                </li>
                <li>
                    <label class="checkbox">
                        <input type="checkbox" bind:checked={requireCaptcha} />
                        <span>Require captcha</span>
                    </label>
                </li>
                <li>
                    <label class="checkbox">
                        <input type="checkbox" bind:checked={proxyBlock} />
                        <span>Block proxies</span>
                    </label>
                </li>
                <li>
                    <label class="checkbox">
                        <input
                            type="checkbox"
                            bind:checked={allowMultipleSubmissions}
                        />
                        <span>Allow multiple submissions</span>
                    </label>
                </li>
            </ul>

            <nav class="wrap" style="margin: 1em 0;">
                <div class="field label border">
                    <input
                        bind:value={surveyCloses}
                        type="date"
                        class="active"
                        min={new Date().toISOString().split("T")[0]}
                    />
                    <label class="active" for="date">Submission cutoff</label>
                </div>
            </nav>

            <label class="color">
                <input
                    bind:value={surveyTheme}
                    on:change={previewTheme}
                    type="color"
                />
                <span>Theme color</span>
            </label>

            <nav class="wrap">
                <button on:click={onPublish}>Create survey</button>
            </nav>
        </article>

        <Title bind:title={surveyTitle} bind:description={surveyDescription} />

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
    ul {
        list-style: none;
    }
</style>
