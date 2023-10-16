<script lang="ts">
    import type { rawChoice } from "../types";

    // Placeholder so component doesnt error if passed.
    export let choices: rawChoice[] = [];

    export let readOnly: boolean = false;
    export let answer: string | number | string[] | null | undefined = null;
</script>

<div class="field border survey-response large">
    <input
        type="text"
        readonly={readOnly}
        bind:value={answer}
        placeholder="Please enter your answer"
    />
</div>
