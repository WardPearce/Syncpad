<script lang="ts">
    import { selectOnClick } from "./helpers";

    export let choices: string[] = [];

    let choiceCount = 1;
    function addChoice() {
        choices = [...choices, `Choice ${choiceCount++}`];
    }

    function removeChoice(index: number) {
        choices = choices.filter((_, i) => i !== index);
    }

    addChoice();
</script>

{#each choices as choice, index}
    <nav style="margin-top: 1em;">
        <div class="checkbox">
            <input disabled type="checkbox" />
            <span />
        </div>
        <div class="field border small">
            <input type="text" bind:value={choice} on:click={selectOnClick} />
        </div>
        <button
            class="square border tertiary-border tertiary-text round"
            disabled={choices.length === 1}
            on:click={() => removeChoice(index)}
        >
            <i>delete</i>
        </button>
    </nav>
{/each}

<button on:click={addChoice} style="margin-top: 1em;">
    <i>add</i>
    <span>New Choice</span>
</button>
