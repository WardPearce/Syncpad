<script lang="ts">
    import { onMount } from "svelte";
    import { navigate } from "svelte-navigator";
    import { listTrustedCanaries, saveCanaryAsTrusted } from "../lib/canary";

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
                            try {
                                const jsonData: any = JSON.parse(fileContent);
                                for (const [
                                    domain,
                                    publicKeyHash,
                                ] of Object.entries(jsonData)) {
                                    if (
                                        typeof publicKeyHash === "string" &&
                                        !(domain in canaries)
                                    ) {
                                        await saveCanaryAsTrusted(
                                            domain,
                                            publicKeyHash
                                        );
                                    }
                                }
                            } catch {}
                        } catch (error) {}
                    }
                });

                reader.readAsText(file);
            }
        });

        input.click();

        showImportWarning = false;
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

    let showImportWarning = false;
    let canaries: Record<string, string> = {};
    onMount(async () => {
        canaries = await listTrustedCanaries();
    });
</script>

<h3>Trusted canaries</h3>
<button disabled={!canaries} class="small" on:click={exportCanaries}
    >Export canaries</button
>
<button class="small" on:click={() => (showImportWarning = true)}
    >Import canaries</button
>

<dialog class="modal small surface-variant" class:active={showImportWarning}>
    <h5>Import trusted canaries</h5>
    <p>
        <span style="font-weight: bold;">Important Warning:</span> It is absolutely
        crucial to import canaries exclusively from a trusted source. Ideally, rely
        solely on your own backup. Under no circumstances should you import any canaries
        from individuals who insist that you must do so.
    </p>
    <nav class="right-align">
        <button class="border" on:click={() => (showImportWarning = false)}
            >Cancel</button
        >
        <button on:click={importCanaries}>Continue</button>
    </nav>
</dialog>

{#if Object.keys(canaries).length > 0}
    {#each Object.entries(canaries) as [domain, publicKeyHash]}
        <article>
            <nav>
                <h5>{domain}</h5>
                <button
                    on:click={() => navigate(`/c/${domain}/${publicKeyHash}`)}
                    >Visit canary</button
                >
            </nav>
        </article>
    {/each}
{:else}
    <h6>No trusted canaries</h6>
{/if}

<style>
    @media only screen and (max-width: 600px) {
        nav {
            flex-direction: column;
        }
    }
</style>
