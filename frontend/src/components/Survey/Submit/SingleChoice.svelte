<script lang="ts">
    import type { rawChoice } from "../types";

    export let choices: rawChoice[];
    export let answer: number | number[] | string | null = null;

    function onChoiceSelect(choice: number) {
        if (answer === choice) answer = null;
        else answer = choice;
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <label class="radio">
            <input
                type="radio"
                on:click={() => onChoiceSelect(choice.id)}
                name={choice.choice}
                checked={answer === choice.id}
            />
            <span>{choice.choice}</span>
        </label>
    </nav>
{/each}
