<script lang="ts">
    import { selectOnClick } from "./helpers";

    export let title: string;
</script>

<article class="extra-large-width">
    <div class="field fill extra">
        <input type="text" bind:value={title} on:click={selectOnClick} />
    </div>
    <div class="field fill textarea label large">
        <textarea />
        <label for="desc">Description</label>
    </div>
</article>

<style>
    article {
        border-top: 1em solid var(--primary);
    }
</style>
