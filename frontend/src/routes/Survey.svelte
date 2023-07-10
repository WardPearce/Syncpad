<script lang="ts">
    import { onMount } from "svelte";
    import { normalizeSurveyQuestions } from "../components/Survey/helpers";
    import type { rawQuestion } from "../components/Survey/types";
    import apiClient from "../lib/apiClient";
    import type { SurveyPublicModel } from "../lib/client";
    import { base64Decode } from "../lib/crypto/codecUtils";
    import hash from "../lib/crypto/hash";
    import secretKey from "../lib/crypto/secretKey";
    import signatures from "../lib/crypto/signatures";

    export let surveyId: string;
    export let signPublicKeyHash: string;

    const b64EncodedRawKey: string = location.hash.substring(1);

    let surveyLoading = true;

    let survey: SurveyPublicModel;

    let rawTitle: string;
    let rawDescription: string | undefined;
    let rawQuestions: rawQuestion[] = [];
    let rawPublicKey: Uint8Array;
    let rawSignPublicKey: Uint8Array;

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

        surveyLoading = false;
    });
</script>
