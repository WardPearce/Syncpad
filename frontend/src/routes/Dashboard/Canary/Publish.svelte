<script lang="ts">
    export let domainName: string;

    const statementTemplates = {
        "Operation as normal":
            "I hereby declare that as of {currentDate}, I am still in complete control of {domain} and all its associated data. As the owner and administrator of the website, I have not received any subpoenas or warrants for data, nor have I received any gag order limiting me from informing users as such, and I remain committed to protecting the privacy and security of all users of my website. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Canary provider moved":
            "I hereby declare that as of {currentDate}, I am issuing this statement to inform users that we are moving our canary from Purplix.io to another canary service. As the owner and administrator of the website, I affirm that this change is solely related to the canary service provider and does not indicate any compromise of user data or any legal demands received. The new canary service will provide continued transparency and timely updates regarding the status of user privacy and security.",
        "Warrents - No user data compromised":
            "I hereby declare that as of {currentDate}, I have received a warrant for data related to {domain}. However, I can confirm that no user data has been compromised as a result of this warrant. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Warrents - User data compromised":
            "I hereby declare that as of {currentDate}, I have received a warrant for data related to {domain}. User data has been compromised as a result of this warrant. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Subpoenas - No user data compromised":
            "I hereby declare that as of {currentDate}, I have received a subpoena for data related to {domain}. However, I can confirm that no user data has been compromised as a result of this subpoena. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Subpoenas - User data compromised":
            "I hereby declare that as of {currentDate}, I have received a subpoena for data related to {domain}. User data has been compromised as a result of this subpoena. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Raids - No user data compromised":
            "I hereby declare that as of {currentDate}, there has been a raid or seizure of data related to {domain}. However, I can confirm that no user data has been compromised as a result of this raid. I am diligently protecting the privacy and security of all users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Raids - User data compromised":
            "I hereby declare that as of {currentDate}, there has been a raid or seizure of data related to {domain}. User data has been compromised as a result of this raid. I am taking immediate actions to mitigate the impact, investigate the incident, and notify affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Trap and trace orders":
            "I hereby declare that as of {currentDate}, I have received trap and trace orders related to {domain}. User communication may have been monitored or intercepted as a result of these orders. I am actively working to address the situation, protect user privacy, and ensure the integrity of the platform. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
        "Blackmail or extortion":
            "I hereby declare that as of {currentDate}, there have been instances of blackmail or extortion targeting {domain} or its administrators. I am taking immediate actions to investigate and mitigate the situation, as well as provide support to affected users. This statement will be reviewed and updated as necessary on or before {nextCanary}.",
    };

    let statement = statementTemplates["Operation as normal"].toString();
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
                <a>Canary provider moved</a>
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
