<article>
    <div class="grid">
        <div class="s12 m6 l7">
            <div class="field border large fill">
                <input type="text" value="Untitled Question" />
            </div>
        </div>
        <div class="s12 m6 l3">
            <div class="field suffix large border">
                <select>
                    <option>Short answer</option>
                    <option>Paragraph</option>
                    <option>Multiple choice</option>
                    <option>Checkbox</option>
                </select>
                <i>arrow_drop_down</i>
            </div>
        </div>
    </div>
    <article class="surface-variant">
        <nav class="right-align">
            <button class="border">
                <i>add</i>
                <span>Add Description</span>
            </button>

            <button class="border">
                <i>done_all</i>
                <span>Regex</span>
            </button>

            <button class="square border tertiary-border tertiary-text round">
                <i>delete</i>
                <div class="tooltip">Delete question</div>
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
    @media only screen and (max-width: 800px) {
        nav {
            align-items: start;
            flex-direction: column;
        }
    }
</style>
