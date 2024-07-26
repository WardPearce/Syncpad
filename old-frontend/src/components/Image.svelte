<script lang="ts">
    import { onMount } from "svelte";

    export let src: string;
    export let alt = "Image";
    export let size = "small";

    let loaded = false;
    let failed = false;
    let loading = false;

    onMount(() => {
        const img = new Image();
        img.src = src;
        loading = true;

        img.onload = () => {
            loading = false;
            loaded = true;
        };
        img.onerror = () => {
            loading = false;
            failed = true;
        };
    });
</script>

{#if loaded}
    <img {src} {alt} class={size} />
{:else if failed}
    <p>Failed to load</p>
{:else if loading}
    <progress class={`circle ${size}`} />
{/if}
