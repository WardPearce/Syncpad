<script lang="ts">
    import type { rawChoice } from "../types";

    // Placeholder so component doesnt error if passed.
    export let choices: rawChoice[] = [];

    export let answer: number | number[] | string | null = null;
</script>

<div class="field border survey-response textarea extra">
    <textarea bind:value={answer} placeholder="Please enter your answer" />
</div>
