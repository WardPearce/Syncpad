<script lang="ts">
    import { SurveyQuestionModel } from "../../../lib/client";
    import { selectOnClick } from "../helpers";
    import type { rawChoice } from "../types";
    import MultipleChoice from "./MultipleChoice.svelte";
    import Paragraph from "./Paragraph.svelte";
    import ShortAnswer from "./ShortAnswer.svelte";
    import SingleChoice from "./SingleChoice.svelte";

    export let removeQuestion: (index: number) => void;
    export let duplicateQuestion: (index: number) => void;
    export let startDrag: () => void;
    export let stopDrag: () => void;
    export let questionId: number;
    export let question: string;
    export let regex: string | null = null;
    export let description: string | null = null;
    export let required: boolean = false;
    export let type: SurveyQuestionModel.type;
    export let choices: rawChoice[] = [];

    let addDescription: boolean = false;
    let regexDialogOpen: boolean = false;
    const regexPatterns = {
        Email: /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/,
        Number: /^\d+$/,
        Street: /^\d+\s[A-z]+\s[A-z]+/,
        Website: /^https?:\/\/[\w-\.]+\.[a-z]{2,4}\/?$/,
        "Card number": /^\d{4}\s\d{4}\s\d{4}\s\d{4}$/,
        Cvs: /^\d{3}$/,
        Date: /^\d{2}\/\d{2}\/\d{4}$/,
        "Card name": /^[A-z]+\s[A-z]+$/,
        "Zip code": /^\d{5}$/,
        None: null,
    };

    const answerTypes = {
        0: {
            component: ShortAnswer,
            name: "Short Answer",
        },
        1: {
            component: Paragraph,
            name: "Paragraph",
        },
        2: {
            component: MultipleChoice,
            name: "Multiple Choice",
        },
        3: {
            component: SingleChoice,
            name: "Single Choice",
        },
    };
    const regexAllowed = ["Proxy<ShortAnswer>", "Proxy<Paragraph>"];
    let selectedAnswer = answerTypes[type].component;

    function setRegex(event: Event) {
        const target = event.target as HTMLSelectElement;
        regex = regexPatterns[target.value];
    }

    function changeAnswer(typeTarget: number) {
        choices = [];
        type = typeTarget;
        selectedAnswer = answerTypes[typeTarget].component;
    }
</script>

<div>
    <dialog class:active={regexDialogOpen}>
        <h5>Input validation</h5>
        <div>
            <div class="field label border">
                <input type="text" bind:value={regex} />
                <label for="regex">Regex pattern</label>
            </div>
            <div class="field suffix border">
                <select on:change={setRegex}>
                    <option value="" disabled selected
                        >Predefined patterns</option
                    >
                    {#each Object.keys(regexPatterns) as regexPattern}
                        <option>{regexPattern}</option>
                    {/each}
                </select>
                <i>arrow_drop_down</i>
            </div>
        </div>
        <nav class="right-align">
            <button
                class="border"
                on:click={() => ((regexDialogOpen = false), (regex = null))}
                >Cancel</button
            >
            <button on:click={() => (regexDialogOpen = false)}>Confirm</button>
        </nav>
    </dialog>

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
                    <input
                        type="text"
                        bind:value={question}
                        on:click={selectOnClick}
                    />
                </div>
            </div>
            <div class="s12 m6 l4">
                <div class="field suffix large border">
                    <select>
                        {#each Object.keys(answerTypes) as answer}
                            <option
                                on:click={() => changeAnswer(Number(answer))}
                                selected={SurveyQuestionModel.type[answer] ===
                                    type}>{answerTypes[answer].name}</option
                            >
                        {/each}
                    </select>
                    <i>arrow_drop_down</i>
                </div>
            </div>
        </div>
        <div>
            {#if addDescription || description !== null}
                <div class="field label textarea fill large">
                    <textarea bind:value={description} />
                    <label for="desc">Description</label>
                </div>
            {:else}
                <button
                    class="border small"
                    on:click={() => (addDescription = true)}
                >
                    Add description
                </button>
            {/if}
        </div>
        <svelte:component this={selectedAnswer} bind:choices />
        <article class="surface-variant">
            <nav class="right-align">
                <button
                    class="square border tertiary-border tertiary-text round"
                    on:click={() => removeQuestion(questionId)}
                >
                    <i>delete</i>
                    <div class="tooltip">Delete question</div>
                </button>

                {#if regexAllowed.includes(selectedAnswer.name)}
                    <button
                        class="square border round"
                        on:click={() => (regexDialogOpen = true)}
                    >
                        <i>rule</i>
                        <div class="tooltip">Question validation</div>
                    </button>
                {/if}

                <button
                    class="square border round"
                    on:click={() => duplicateQuestion(questionId)}
                >
                    <i>content_copy</i>
                    <div class="tooltip">Duplicate question</div>
                </button>

                <label class="switch">
                    <input type="checkbox" bind:checked={required} />
                    <span style="padding-left: .3em;">Required</span>
                </label>
            </nav>
        </article>
    </article>
</div>

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
