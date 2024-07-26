<script lang="ts">
    import { selectOnClick } from "../helpers";

    export let title: string;
    export let description: string;
</script>

<article class="extra-large-width survey-title">
    <div class="field fill extra">
        <input type="text" bind:value={title} on:click={selectOnClick} />
    </div>
    <div class="field fill textarea label large">
        <textarea bind:value={description} />
        <label for="desc">Description</label>
    </div>
</article>
