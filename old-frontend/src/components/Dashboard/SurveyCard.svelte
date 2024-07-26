<script lang="ts">
    import sodium from "libsodium-wrappers-sumo";
    import { onMount } from "svelte";
    import { navigate } from "svelte-navigator";
    import apiClient from "../../lib/apiClient";
    import type { SurveyModel } from "../../lib/client";
    import { base64Encode } from "../../lib/crypto/codecUtils";
    import { hashBase64Encode } from "../../lib/crypto/hash";
    import secretKey, { SecretkeyLocation } from "../../lib/crypto/secretKey";
    import { relativeDate } from "../../lib/date";
    import { concat } from "../../lib/misc";

    export let survey: SurveyModel;

    let isLoading = true;
    let rawTitle: string;
    let rawDescription: string | null | undefined;
    let rawKey: Uint8Array;

    onMount(() => {
        isLoading = true;
        rawKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.secret_key.iv,
            survey.secret_key.cipher_text
        ) as Uint8Array;

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

        isLoading = false;
    });

    function goToSurvey() {
        navigate(shareLink());
    }

    function shareLink(): string {
        const privateKey = secretKey.decrypt(
            SecretkeyLocation.localKeychain,
            survey.sign_keypair.iv,
            survey.sign_keypair.cipher_text
        );
        const publicKey = sodium.crypto_sign_ed25519_sk_to_pk(
            privateKey as Uint8Array
        );
        return `/s/${survey.id}/${hashBase64Encode(
            publicKey,
            true
        )}#${base64Encode(rawKey, true)}`;
    }

    async function deleteSurvey() {
        await apiClient.survey.controllersSurveySurveyIdDeleteDeleteSurvey(
            survey.id
        );
        isLoading = true;
    }
</script>

{#if !isLoading}
    <div class="s12 m6 l4">
        <article>
            <nav class="wrap" style="margin-bottom: 1em;">
                <button class="link-button" on:click={goToSurvey}>
                    <h6>{concat(rawTitle, 12)}</h6>
                </button>
                <p>{relativeDate(survey.created)}</p>
            </nav>
            {#if rawDescription}
                <p>{concat(rawDescription, 40)}</p>
            {:else}
                <p>No description</p>
            {/if}
            <nav class="wrap">
                <button
                    on:click={() =>
                        navigate(`/dashboard/survey/results/${survey.id}`)}
                    >Results</button
                >
                <button class="border" on:click={deleteSurvey}>Delete</button>
            </nav>
        </article>
    </div>
{/if}
