<script lang="ts">
    import type { rawChoice } from "../types";

    export let choices: rawChoice[];
    export let answer: number | number[] | string | null;
    export let readOnly: boolean = false;

    function handleCheckboxChange(event: Event, choice: rawChoice) {
        if (readOnly) {
            (event.target as HTMLInputElement).checked = (
                answer as number[]
            ).includes(choice.id);
            return;
        }
        if ((event.target as HTMLInputElement).checked) {
            // Append choice.id to answer
            if (Array.isArray(answer)) {
                answer = [...answer, choice.id];
            } else {
                answer = [choice.id];
            }
        } else {
            // Remove choice.id from answer
            if (Array.isArray(answer)) {
                answer = answer.filter(
                    (id: number | string) => id !== choice.id
                );
            }
        }
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <label class="checkbox">
            <input
                type="checkbox"
                checked={answer instanceof Array && answer.includes(choice.id)}
                on:change={(event) => handleCheckboxChange(event, choice)}
            />
            <span>{choice.choice}</span>
        </label>
    </nav>
{/each}
