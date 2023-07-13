<script lang="ts">
    export let choices: string[];
    export let answer: string;

    function onChoiceSelect(choice: string) {
        answer = choice;
    }
</script>

{#each choices as choice}
    <nav style="margin-top: 1em;">
        <label class="checkbox">
            <input type="checkbox" on:click={() => onChoiceSelect(choice)} />
            <span>{choice}</span>
        </label>
    </nav>
{/each}
