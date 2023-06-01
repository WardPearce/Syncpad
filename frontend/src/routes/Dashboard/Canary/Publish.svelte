<script lang="ts">
    export let domainName: string;

    const statementTemplates = {
        operationAsNormal:
            "I hereby declare that as of {currentDate}, I am still in complete control of {domain} and all its associated data. As the owner and administrator of the website, I have not received any subpoenas or warrants for data, nor have I received any gag order limiting me from informing users as such, and I remain committed to protecting the privacy and security of all users of my website. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
    };

    let statement = statementTemplates.operationAsNormal.toString();
</script>

<article>
    <h3>Publish Canary</h3>
    <button>
        <span>Frequency</span>
        <i>arrow_drop_down</i>
        <menu>
            <a>Daily</a>
            <a>Weekly</a>
            <a>Fortnightly</a>
            <a>Montly</a>
            <a>Yearly</a>
        </menu>
    </button>

    <button>
        <span>Concern level</span>
        <i>arrow_drop_down</i>
        <menu>
            <a>None</a>
            <a>Mild</a>
            <a>Moderate</a>
            <a>Serve</a>
        </menu>
    </button>

    <div class="field textarea label border extra" style="margin-bottom: 0;">
        <textarea bind:value={statement} />
        <label for="statement">Statement</label>
    </div>
    <nav class="right-align" style="margin-bottom: 1em;">
        <button>
            <span>Statement templates</span>
            <i>arrow_drop_down</i>
            <menu>
                <a>Operation as normal</a>
                <a>Warrents - No user data compromised</a>
                <a>Warrents - User data compromised</a>
                <a>Subpoenas - No user data compromised</a>
                <a>Subpoenas - User data compromised</a>
                <a>Raids - No user data compromised</a>
                <a>Raids - User data compromised</a>
                <a>Trap and trace orders</a>
                <a>Blackmail or extortion</a>
            </menu>
        </button>
    </nav>
</article>
