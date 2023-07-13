<script lang="ts">
    export let answer: string = "";
</script>

<div class="field border survey-response textarea extra">
    <textarea bind:value={answer} placeholder="Please enter your answer" />
</div>
