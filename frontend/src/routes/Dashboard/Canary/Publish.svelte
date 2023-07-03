<script lang="ts">
    import * as idbKeyval from "idb-keyval";
    import { onMount } from "svelte";
    import OtpInput from "../../../components/OtpInput.svelte";
    import apiClient from "../../../lib/apiClient";
    import { goToCanary } from "../../../lib/canary";
    import {
        ApiError,
        CreateCanaryWarrantModel,
        PublishCanaryWarrantModel,
    } from "../../../lib/client";
    import hash from "../../../lib/crypto/hash";
    import secretKey, {
        SecretkeyLocation,
    } from "../../../lib/crypto/secretKey";
    import signatures from "../../../lib/crypto/signatures";

    export let domainName: string;

    let statementTemplates = {
        Blank: "",
        "Operation as normal":
            "I hereby declare that as of {currentDate}, I am still in complete control of {domain} and all its associated data. As the owner and administrator of the website, I have not received any subpoenas or warrants for data, nor have I received any gag order limiting me from informing users as such, and I remain committed to protecting the privacy and security of all users of my website. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Canary provider moved": `I hereby declare that as of {currentDate}, I am issuing this statement to inform users that we are moving our canary from ${
            import.meta.env.VITE_SITE_NAME
        } to another canary service. As the owner and administrator of the website, I affirm that this change is solely related to the canary service provider and does not indicate any compromise of user data or any legal demands received. The new canary service will provide continued transparency and timely updates regarding the status of user privacy and security.`,
        "Warrents - No user data compromised":
            "I hereby declare that as of {currentDate}, I have received a warrant for data related to {domain}. However, I can confirm that no user data has been compromised as a result of this warrant. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Warrents - User data compromised":
            "I hereby declare that as of {currentDate}, I have received a warrant for data related to {domain}. User data has been compromised as a result of this warrant. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Subpoenas - No user data compromised":
            "I hereby declare that as of {currentDate}, I have received a subpoena for data related to {domain}. However, I can confirm that no user data has been compromised as a result of this subpoena. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Subpoenas - User data compromised":
            "I hereby declare that as of {currentDate}, I have received a subpoena for data related to {domain}. User data has been compromised as a result of this subpoena. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Raids - No user data compromised":
            "I hereby declare that as of {currentDate}, there has been a raid or seizure of data related to {domain}. However, I can confirm that no user data has been compromised as a result of this raid. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Raids - User data compromised":
            "I hereby declare that as of {currentDate}, there has been a raid or seizure of data related to {domain}. User data has been compromised as a result of this raid. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Trap and trace orders":
            "I hereby declare that as of {currentDate}, I have received trap and trace orders related to {domain}. User communication may have been monitored or intercepted as a result of these orders. I am actively working to address the situation, protect user privacy, and ensure the integrity of the platform. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Blackmail or extortion":
            "I hereby declare that as of {currentDate}, there have been instances of blackmail or extortion targeting {domain} or its administrators. I am taking immediate actions to investigate and mitigate the situation, as well as provide support to affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
    } as Record<string, string>;

    let statement = statementTemplates["Operation as normal"].toString();
    let nextCanary = CreateCanaryWarrantModel.next.FORTNIGHT;
    let canaryConcern = PublishCanaryWarrantModel.concern.NONE;
    let documents: FileList;

    let customTemplate = false;
    let publishModelActive = false;
    let saveModelActive = false;
    let customTemplateLabel = "";
    let enteredDomain = "";
    let errorMsg = "";

    onMount(async () => {
        const customTemplates = await idbKeyval.get("customCanaryTemplates");
        if (customTemplates) {
            statementTemplates = {
                ...customTemplates,
                ...statementTemplates,
            };
        }
    });

    async function onPublish(otpCode: string) {
        if (enteredDomain !== domainName) {
            errorMsg = "Domain name does not match";
            return;
        }

        try {
            const canary =
                await apiClient.canary.controllersCanaryDomainGetCanary(
                    domainName
                );

            const createdWarrant =
                await apiClient.warrant.controllersCanaryDomainCreateWarrantCreateWarrant(
                    domainName,
                    otpCode,
                    { next: nextCanary }
                );

            let latestBlock: string;
            try {
                latestBlock = await (
                    await fetch(
                        `${
                            import.meta.env.VITE_BLOCKSTREAM_API
                        }/blocks/tip/hash`
                    )
                ).text();
            } catch {
                errorMsg = `Failed to fetch latest BTC block from ${
                    import.meta.env.VITE_BLOCKSTREAM_API
                }`;
                return;
            }

            const formattedStatement = statement
                .replaceAll("{domain}", domainName)
                .replaceAll("{nextCanary}", createdWarrant.next_canary)
                .replaceAll("{currentDate}", createdWarrant.issued);

            let documentHashes: Record<string, string> = {};

            if (documents) {
                let documentPromises: Promise<Response>[] = Array.from(
                    documents
                ).map(async (document) => {
                    const docHash = hash.hashBase64Encode(
                        new Uint8Array(await document.arrayBuffer()),
                        true
                    );

                    documentHashes[document.name] = docHash;

                    return apiClient.document.controllersCanaryWarrantWarrantIdDocumentHashUploadDocument(
                        createdWarrant._id,
                        docHash,
                        [document]
                    );
                });

                await Promise.all(documentPromises);
            }

            await apiClient.warrant.controllersCanaryWarrantWarrantIdPublishPublish(
                createdWarrant._id,
                {
                    statement: formattedStatement,
                    concern: canaryConcern,
                    btc_latest_block: latestBlock,
                    signature: signatures.signHash(
                        secretKey.decrypt(
                            SecretkeyLocation.localKeychain,
                            canary.keypair.iv,
                            canary.keypair.cipher_text
                        ) as Uint8Array,
                        JSON.stringify({
                            btc_latest_block: latestBlock,
                            statement: formattedStatement,
                            concern: canaryConcern,
                            next_canary: createdWarrant.next_canary,
                            issued: createdWarrant.issued,
                            domain: domainName,
                            id: createdWarrant._id,
                            document_hashes: documentHashes,
                        })
                    ),
                }
            );

            goToCanary(canary);
        } catch (error) {
            if (error instanceof ApiError) errorMsg = error.body.detail;
            else errorMsg = error.message;
        }
    }

    function onStatementChange() {
        customTemplate = true;
    }

    async function saveCustomTemplate() {
        if (customTemplateLabel) {
            const toSave = {};
            const customTemplates = await idbKeyval.get(
                "customCanaryTemplates"
            );
            if (customTemplates) {
                Object.assign(toSave, customTemplates);
            }

            toSave[customTemplateLabel] = statement;

            statementTemplates = {
                [customTemplateLabel]: statement,
                ...statementTemplates,
            };

            await idbKeyval.set("customCanaryTemplates", toSave);

            customTemplate = false;
            saveModelActive = false;
            customTemplateLabel = "";
        }
    }
</script>

<dialog class="surface-variant" class:active={saveModelActive}>
    <h5>Save custom template</h5>
    <form on:submit|preventDefault={saveCustomTemplate}>
        <div class="field label fill border">
            <input type="text" bind:value={customTemplateLabel} />
            <label for="title">Template label</label>
        </div>

        <nav class="right-align">
            <button
                type="button"
                class="border"
                on:click={() => (
                    (saveModelActive = false), (customTemplateLabel = "")
                )}>Cancel</button
            >
            <button>Save</button>
        </nav>
    </form>
</dialog>

<dialog class="surface-variant" class:active={publishModelActive}>
    <h5>Publish canary</h5>
    {#if errorMsg}
        <div class="error" style="padding: 0.3em 1em;">
            <p>{errorMsg}</p>
        </div>
    {/if}

    <p>Please type the domain "{domainName}" to confirm.</p>
    <div
        class="field label fill border"
        class:invalid={enteredDomain !== "" && enteredDomain !== domainName}
    >
        <input type="text" bind:value={enteredDomain} />
        <label for="domain-confirm">Enter domain</label>
    </div>
    <OtpInput onOtpEnter={onPublish} />
    <button
        type="button"
        class="border"
        style="margin-top: 2em;"
        on:click={() => ((publishModelActive = false), (enteredDomain = ""))}
        >Cancel</button
    >
</dialog>

<h3>Publish for {domainName}</h3>
<article>
    <form on:submit|preventDefault={() => (publishModelActive = true)}>
        <h6>Next canary</h6>
        <nav class="wrap" style="margin-top: 0;">
            {#each Object.values(CreateCanaryWarrantModel.next) as next}
                <button
                    class="chip round primary"
                    type="button"
                    disabled={nextCanary === next}
                    on:click={() => (nextCanary = next)}
                >
                    {#if next !== CreateCanaryWarrantModel.next.TOMORROW}
                        In a {next}
                    {:else}
                        Tomorrow
                    {/if}
                </button>
            {/each}
        </nav>

        <h6>Concern level</h6>
        <nav class="wrap" style="margin-top: 0;">
            {#each Object.values(PublishCanaryWarrantModel.concern) as concernLvl}
                <button
                    class="chip round primary"
                    type="button"
                    style="text-transform: capitalize;"
                    disabled={canaryConcern === concernLvl}
                    on:click={() => (canaryConcern = concernLvl)}
                >
                    {concernLvl}
                </button>
            {/each}
        </nav>

        <h6>Documents</h6>
        <nav style="margin-bottom: 2em;margin-top: 0;">
            <div class="field label suffix border" style="margin-top: 0;">
                <input type="text" />
                <input type="file" multiple={true} bind:files={documents} />
                <label for="files">Files</label>
                <i>attach_file</i>
                <span class="helper"> Max 15MB each - Max 3 files </span>
            </div>
        </nav>

        <h6>Statement</h6>
        <div class="field textarea border extra" style="margin-top: 0;">
            <textarea bind:value={statement} on:input={onStatementChange} />
            <span class="helper"
                ><span style="font-weight: bold;">Formatting:</span>
                {"{nextCanary}"} = date of next canary, {"{currentDate}"}
                = current date & {"{domain}"} = domain</span
            >
        </div>

        <nav class="publish-area">
            <div>
                <button type="button">
                    <span>Statement templates</span>
                    <i>arrow_drop_down</i>
                    <menu>
                        {#each Object.entries(statementTemplates) as [title, template]}
                            <a
                                href="#{title}"
                                on:click={() => (statement = template)}
                                >{title}</a
                            >
                        {/each}
                    </menu>
                </button>
                {#if customTemplate}
                    <button
                        type="button"
                        class="fill"
                        on:click={() => (saveModelActive = true)}
                    >
                        <i>save</i>
                        <span>Save custom template</span>
                    </button>
                {/if}
            </div>
            <button>
                <i>publish</i>
                <span>Publish</span>
            </button>
        </nav>
    </form>
</article>

<style>
    .publish-area {
        margin-bottom: 1em;
        margin-top: 2em;
        justify-content: space-between;
    }

    @media only screen and (max-width: 600px) {
        nav {
            flex-direction: column;
            align-items: flex-start;
        }
    }
</style>
