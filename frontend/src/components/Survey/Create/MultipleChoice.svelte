<script lang="ts">
    import { selectOnClick } from "../helpers";
    import type { rawChoice } from "../types";

    export let choices: rawChoice[] = [];

    let choiceCount = 0;
    function addChoice() {
        choices = [
            ...choices,
            { id: choiceCount++, choice: `Choice ${choiceCount}` },
        ];
    }

    function removeChoice(id: number) {
        choices = choices.filter((choice) => choice.id !== id);
    }

    addChoice();
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <div class="checkbox">
            <input disabled type="checkbox" />
            <span />
        </div>
        <div class="field border small">
            <input
                type="text"
                bind:value={choice.choice}
                on:click={selectOnClick}
            />
        </div>
        <button
            class="square border tertiary-border tertiary-text round"
            disabled={choices.length === 1}
            on:click={() => removeChoice(choice.id)}
        >
            <i>delete</i>
        </button>
    </nav>
{/each}

<button on:click={addChoice} style="margin-top: 1em;">
    <i>add</i>
    <span>New Choice</span>
</button>
