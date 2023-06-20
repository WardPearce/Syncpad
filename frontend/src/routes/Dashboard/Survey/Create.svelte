<script lang="ts">
    let componentDialogOpen = false;
    let surveyStructure = [];

    let surveyTitle = "Untitled Survey";
    let editTitle = false;
</script>

<dialog class="max" class:active={componentDialogOpen}>
    <nav class="right-align">
        <button class="border" on:click={() => (componentDialogOpen = false)}
            >Cancel</button
        >
    </nav>
</dialog>

{#if !editTitle}
    <nav>
        <h3>{surveyTitle}</h3>
        <button class="square round" on:click={() => (editTitle = true)}>
            <i>create</i>
        </button>
    </nav>
{:else}
    <form on:submit|preventDefault={() => (editTitle = false)}>
        <nav style="margin-top: 1em;">
            <div class="field border">
                <input type="text" bind:value={surveyTitle} />
            </div>
            <button class="square round">
                <i>save</i>
            </button>
        </nav>
    </form>
{/if}

<button
    type="button"
    style="margin-top: 1em;"
    on:click={() => (componentDialogOpen = true)}
>
    <i>add</i>
    <span>Add component</span>
</button>
