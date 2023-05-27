<script lang="ts">
    import { get } from "idb-keyval";
    import { onMount } from "svelte";
    import { navigate } from "svelte-navigator";

    let savedCanaries: Record<string, { id: string; publicKey: string }>;
    onMount(async () => {
        const stored = await get("storedCanaries");
        if (stored) {
            savedCanaries = stored;
        } else {
            navigate("/", { replace: true });
        }
    });
</script>

{#if savedCanaries}
    {#each Object.entries(savedCanaries) as [domain, canary]}
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
{/if}

<style>
    @media only screen and (max-width: 600px) {
        nav {
            flex-direction: column;
        }
    }
</style>
