<script lang="ts">
    import { selectOnClick } from "./helpers";

    let choices: string[] = [];

    addChoice();

    function addChoice() {
        choices = [...choices, `Choice ${choices.length + 1}`];
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <div class="radio">
            <input disabled type="radio" />
            <span />
        </div>
        <div class="field border small">
            <input type="text" bind:value={choice} on:click={selectOnClick} />
        </div>
    </nav>
{/each}

<button on:click={addChoice} style="margin-top: 1em;">
    <i>add</i>
    <span>New Choice</span>
</button>
