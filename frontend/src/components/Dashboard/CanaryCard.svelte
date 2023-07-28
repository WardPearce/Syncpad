<script lang="ts">
    import { link, navigate } from "svelte-navigator";
    import { goToCanary } from "../../lib/canary";
    import type { CanaryModel } from "../../lib/client";
    import { concat } from "../../lib/misc";
    import Image from "../Image.svelte";

    export let canary: CanaryModel;
</script>

<div class="s12 m6 l4">
    <article>
        <nav class="wrap">
            <Image
                src={`${canary.logo}`}
                size="small"
                alt={`Logo for ${canary.domain}`}
            />
            {#if canary.domain_verification.completed}
                <button on:click={() => goToCanary(canary)} class="link-button">
                    <h6>{concat(canary.domain)}</h6>
                </button>
            {:else}
                <h6>{concat(canary.domain)}</h6>
            {/if}
        </nav>
        <p style="margin-top: 1em;">{concat(canary.about, 40)}</p>
        <nav>
            {#if canary.domain_verification.completed}
                <a
                    href={`/dashboard/canary/publish/${canary.domain}/`}
                    class="button"
                    use:link>Publish Canary</a
                >
                <button class="border">Edit</button>
            {:else}
                <button
                    on:click={() =>
                        navigate(
                            `/dashboard/canary/verify-site/${canary.domain}/`
                        )}>Verify domain</button
                >
            {/if}
        </nav>
    </article>
</div>
