<script lang="ts">
    import type { rawChoice } from "../types";

    export let choices: rawChoice[];
    export let answer: number | number[] | string | null = null;
    export let readOnly: boolean = false;

    function onChoiceSelect(event: Event, choice: number) {
        if (readOnly) {
            event.preventDefault();
            answer = answer;
            return;
        }
        if (answer === choice) answer = null;
        else answer = choice;
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <label class="radio">
            <input
                type="radio"
                on:click={(event) => onChoiceSelect(event, choice.id)}
                name={choice.choice}
                checked={answer === choice.id}
            />
            <span>{choice.choice}</span>
        </label>
    </nav>
{/each}
