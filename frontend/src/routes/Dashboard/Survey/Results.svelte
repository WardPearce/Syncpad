<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import apiClient from "../../../lib/apiClient";
    import type { SurveyModel, SurveyQuestionModel } from "../../../lib/client";
    import publicKey from "../../../lib/crypto/publicKey";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";

    export let surveyId: string;

    interface RawAnswer {
        id: number;
        type: SurveyQuestionModel.type;
        answer: string | string[];
    }

    let survey: SurveyModel;
    let rawAnswers: RawAnswer[][][] = [];

    let ws: WebSocket;
    let wsReconnect = true;

    function createWs(pullHistory: boolean): WebSocket {
        return new WebSocket(
            `ws://${apiClient.request.config.BASE.replace(
                "http://",
                ""
            ).replace(
                "http://",
                ""
            )}/controllers/survey/64b891ac33bdfe6a9d418eb6/responses/realtime?pull_history=${pullHistory}`
        );
    }

    onMount(async () => {
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

        ws = createWs(true);

        ws.addEventListener("close", () => {
            if (wsReconnect) {
                ws = createWs(false);
            }
        });

        ws.addEventListener("message", (event) => {
            const data = JSON.parse(JSON.parse(event.data));

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
    });

    onDestroy(() => {
        wsReconnect = false;
        ws.close();
    });
</script>
