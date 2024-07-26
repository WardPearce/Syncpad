<script lang="ts">
    export let title: string;
    export let description: string | null = null;
</script>

<article class="extra-large-width survey-title">
    <h3>{title}</h3>
    {#if description}
        <p>{description}</p>
    {/if}
</article>
