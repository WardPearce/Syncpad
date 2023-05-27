<script lang="ts">
    import { navigate } from "svelte-navigator";
    import {
        savedCanaries,
        updateSavedCanaries,
        type savedCanariesModel,
        type savedCanaryModel,
    } from "../stores";

    let canaries: savedCanariesModel | undefined;
    savedCanaries.subscribe((value) => (canaries = value));

    function importCanaries() {
        const input: HTMLInputElement = document.createElement("input");
        input.type = "file";
        input.accept = ".json";

        input.addEventListener("change", (event: Event) => {
            const file: File | undefined = (event.target as HTMLInputElement)
                .files?.[0];

            if (file) {
                const reader: FileReader = new FileReader();

                reader.addEventListener("load", async () => {
                    const fileContent: string | ArrayBuffer | null =
                        reader.result;

                    if (typeof fileContent === "string") {
                        try {
                            const jsonData: any = JSON.parse(fileContent);
                            for (const [domain, canary] of Object.entries(
                                jsonData
                            )) {
                                if (
                                    canary instanceof Object &&
                                    "id" in canary &&
                                    "publicKey" in canary &&
                                    typeof canary.publicKey === "string" &&
                                    typeof canary.id === "string"
                                ) {
                                    await updateSavedCanaries(
                                        domain,
                                        canary as savedCanaryModel
                                    );
                                }
                            }
                        } catch (error) {}
                    }
                });

                reader.readAsText(file);
            }
        });

        input.click();
    }

    function exportCanaries() {
        const anchor = document.createElement("a");
        const url = window.URL.createObjectURL(
            new Blob([JSON.stringify(canaries, null, 2)], {
                type: "application/json",
            })
        );
        anchor.href = url;
        anchor.download = "purplix-canaries.json";
        anchor.click();
        window.URL.revokeObjectURL(url);
    }
</script>

<h3>Saved canaries</h3>
<button disabled={!canaries} class="small" on:click={exportCanaries}
    >Export canaries</button
>
<button class="small" on:click={importCanaries}>Import canaries</button>

{#if canaries}
    {#each Object.entries(canaries) as [domain, canary]}
        <article>
            <nav>
                <h5>{domain}</h5>
                <button
                    on:click={() =>
                        navigate(`/c/${domain}/${canary.publicKey}`)}
                    >Visit canary</button
                >
            </nav>
        </article>
    {/each}
{:else}
    <p>No saved canaries</p>
{/if}

<style>
    @media only screen and (max-width: 600px) {
        nav {
            flex-direction: column;
        }
    }
</style>
