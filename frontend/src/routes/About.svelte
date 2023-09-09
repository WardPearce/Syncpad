<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { link, navigate } from "svelte-navigator";
    import { get } from "svelte/store";
    import { slide } from "svelte/transition";
    import Logo from "../components/Logo.svelte";
    import { localSecrets, showNav } from "../stores";

    showNav.set(false);

    onDestroy(() => showNav.set(true));

    if (get(localSecrets)) {
        navigate("/dashboard");
    }

    const words = ["customers", "family", "employees", "friends"];
    let wordsIndex = 0;
    let roller: NodeJS.Timer;

    onMount(() => {
        roller = setInterval(() => {
            if (wordsIndex === words.length - 1) wordsIndex = 0;
            else wordsIndex++;
        }, 5000);
    });

    onDestroy(() => {
        clearInterval(roller);
    });
</script>

<article class="nav">
    <nav>
        <div class="logo">
            <Logo />
        </div>
        <div>
            <a use:link href="/register" class="button">Get started</a>
            <a use:link href="/login" class="button secondary">Login</a>
        </div>
    </nav>
</article>

<div class="header">
    {#key wordsIndex}
        <h2>
            Securely survey your&nbsp;<span
                in:slide
                out:slide={{ duration: 0 }}
                style="font-weight: bolder;">{words[wordsIndex]}.</span
            >
        </h2>
        <h6>
            Only&nbsp;<span style="font-weight: bolder;">you</span>&nbsp;can see
            the results, not us, not the government.
        </h6>
    {/key}
</div>

<article>
    <div class="grid">
        <div class="s12 m6 l8">
            <h3>What is {import.meta.env.VITE_SITE_NAME} Survey?</h3>
            <p>
                Purplix Survey is a free & <a
                    target="_blank"
                    referrerpolicy="no-referrer"
                    href="https://github.com/WardPearce/Purplix.io"
                    class="link">open source</a
                > survey tool what can't read your questions & answers.
            </p>

            <h5>How does it work?</h5>
            <h6>Questions, Descriptions & Title encryption</h6>
            <p>
                When you create a survey, we protect your questions with a
                secret key. This key is then stored encrypted in your keychain.
                When you share your survey with others using a link, the key is
                stored in the link for your participants. This ensures that your
                survey questions can only be read by your participants.
            </p>

            <h6>Answers encryption</h6>
            <p>
                Every survey has its own unique key pair. The private key is
                securely stored in your keychain, while the public key is used
                by users to encrypt their answers. Only you have the means to
                decrypt the answers once they are submitted. When you share a
                survey, we include a hash of the public key in the URL to
                prevent main-in-the-middle attacks.
            </p>

            <nav class="wrap left-align">
                <button>Get started</button>
                <button class="secondary">Learn more</button>
            </nav>
        </div>
        <div class="s12 m6 l4 right-align">
            <img
                src="/previews/survey.png"
                height="700px"
                alt="Preview of a car wash survey"
            />
        </div>
    </div>
</article>

<article>
    <div class="grid">
        <div class="s12 m6 l4">
            <img
                src="/previews/canary.png"
                height="700px"
                alt="Preview of a car wash survey"
            />
        </div>
        <div class="s12 m6 l8">
            <h3>What is {import.meta.env.VITE_SITE_NAME} Canary?</h3>
            <p>
                Purplix Canary is a free & <a
                    target="_blank"
                    referrerpolicy="no-referrer"
                    href="https://github.com/WardPearce/Purplix.io"
                    class="link">open source</a
                > warrant canary tool what helps you to build trust with your users.
            </p>
            <p>
                It allows you to inform users cryptographically if your site has
                been compromised, seized or raided by anyone.
            </p>

            <h5>How does it work?</h5>

            <nav class="wrap left-align">
                <button>Get started</button>
                <button class="secondary">Learn more</button>
            </nav>
        </div>
    </div>
</article>

<style>
    nav {
        justify-content: space-between;
    }

    .nav {
        margin-top: 0.2em;
        border-bottom-right-radius: 0;
        border-bottom-left-radius: 0;
    }

    .header {
        height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: var(--primary);
        color: var(--on-primary);
        border-radius: 0 0 0.75rem 0.75rem;
        box-shadow: var(--elevate1);
    }

    .header h6,
    .header h2 {
        margin-top: 0.3em;
        margin-bottom: 0;
    }
</style>
