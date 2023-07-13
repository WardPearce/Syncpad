<script lang="ts">
    export let answer: string = "";
</script>

<div class="field border survey-response large">
    <input
        type="text"
        bind:value={answer}
        placeholder="Please enter your answer"
    />
</div>
