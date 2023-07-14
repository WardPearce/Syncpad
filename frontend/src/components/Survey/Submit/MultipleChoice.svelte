<script lang="ts">
    import type { rawChoice } from "../types";

    export let choices: rawChoice[];
    export let answer: number;

    function onChoiceSelect(choice: number) {
        answer = choice;
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <label class="checkbox">
            <input type="checkbox" on:click={() => onChoiceSelect(choice.id)} />
            <span>{choice.choice}</span>
        </label>
    </nav>
{/each}
