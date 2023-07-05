<script lang="ts">
    import Paragraph from "./Paragraph.svelte";
    import ShortAnswer from "./ShortAnswer.svelte";

    export let removeQuestion: (index: number) => void;
    export let startDrag: () => void;
    export let stopDrag: () => void;
    export let surveyId: number;

    const questions = {
        "Short answer": ShortAnswer,
        Paragraph: Paragraph,
    };
    let selectedAnswer = ShortAnswer;

    function changeAnswer(event: Event) {
        const target = event.target as HTMLSelectElement;
        selectedAnswer = questions[target.value];
    }
</script>

<article class="extra-large-width">
    <div
        class="drag-area"
        on:mousedown={startDrag}
        on:touchstart={startDrag}
        on:mouseup={stopDrag}
        on:touchend={stopDrag}
    >
        <i>drag_handle</i>
    </div>
    <div class="grid">
        <div class="s12 m6 l8">
            <div class="field large fill">
                <input type="text" value="Untitled Question" />
            </div>
        </div>
        <div class="s12 m6 l4">
            <div class="field suffix large border">
                <select on:change={changeAnswer}>
                    {#each Object.keys(questions) as question}
                        <option>{question}</option>
                    {/each}
                </select>
                <i>arrow_drop_down</i>
            </div>
        </div>
    </div>
    <svelte:component this={selectedAnswer} />
    <article class="surface-variant">
        <nav class="right-align">
            <button
                class="square border tertiary-border tertiary-text round"
                on:click={() => removeQuestion(surveyId)}
            >
                <i>delete</i>
                <div class="tooltip">Delete question</div>
            </button>

            <button class="square border round">
                <i>rule</i>
                <div class="tooltip">Question validation</div>
            </button>

            <button class="square border round">
                <i>content_copy</i>
                <div class="tooltip">Duplicate question</div>
            </button>

            <label class="switch">
                <input type="checkbox" />
                <span style="padding-left: .3em;">Required</span>
            </label>
        </nav>
    </article>
</article>

<style>
    .drag-area {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 1em;
        width: 100%;
        user-select: none;
    }

    .drag-area:hover {
        cursor: grab;
    }

    @media only screen and (max-width: 360px) {
        nav {
            align-items: start;
            flex-direction: column;
        }
    }
</style>
