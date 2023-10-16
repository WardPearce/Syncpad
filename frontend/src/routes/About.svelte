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

    const words = ["customers", "friends", "employees", "audience"];
    let wordsIndex = 0;
    let roller: NodeJS.Timer;

    onMount(() => {
        roller = setInterval(() => {
            if (wordsIndex === words.length - 1) wordsIndex = 0;
            else wordsIndex++;
        }, 5000);
    });

    onDestroy(() => {
        clearInterval(Number(roller));
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

<div class="header" transition:slide>
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

            <p>
                With traditional surveys you are one data breach, one rouge
                employee or one government warrant away from all your user's
                data being exposed. Purplix uses modern encryption techniques to
                keep your user's data away from any actors.
            </p>

            <h5>How does it work?</h5>
            <h6>Questions, Descriptions & Title encryption</h6>
            <p>
                When you create a survey, we encrypt your title, descriptions &
                questions with a secret key. This key is then stored encrypted
                in your keychain. When you share your survey with others using a
                link, the key is stored in the link for your participants. This
                ensures that your survey questions can only be read by your
                participants.
            </p>

            <h6>Answers encryption</h6>
            <p>
                Every survey has its own unique key pair. The private key is
                securely stored in your keychain, while the public key is used
                by users to encrypt their answers. Only you have the means to
                decrypt the answers once they are submitted. When you share a
                survey, we include a hash of the public key in the URL to
                prevent man-in-the-middle attacks.
            </p>

            <h6>Preventing spam & multiple submissions</h6>
            <p>
                Survey creators can opt-in to use VPN blocking, requiring a
                Purplix account or IP blocking. IP blocking works by storing a
                hash of the IP salted with a key not stored by Purplix,
                minimizing the attack surface of tracking submission locations,
                these IP hashes are only stored for 7 days or until the survey
                closes. Users will always be informed when any of these features
                are enabled.
            </p>

            <nav class="wrap left-align">
                <a use:link href="/register" class="button">Get started</a>
            </nav>
        </div>
        <div class="s12 m6 l4 right-align site-preview">
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
        <div class="s12 m6 l4 site-preview">
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
            <h6>Site verification</h6>
            <p>
                Purplix uses DNS records to verify the domain the canary is for,
                giving your users confidence they are trusting the right people.
            </p>

            <h6>Canary signatures</h6>
            <p>
                Each domain is associated with a unique key pair. The private
                key is generated locally and securely stored within the owner's
                keychain. When a user visits a canary from a specific domain for
                the first time, their private key is used to sign the public
                key. This signed version of the public key is then automatically
                employed for subsequent visits, effectively mitigating
                man-in-the-middle attacks and ensuring the trustworthiness of
                canary statements from the respective domain.
            </p>

            <h6>Files</h6>
            <p>
                Canaries can include signed documents to help users further
                understand a situation.
            </p>

            <h6>Notifications</h6>
            <p>
                Users are automatically notified on the event of a new statement
                being published.
            </p>

            <nav class="wrap left-align">
                <a use:link href="/register" class="button">Get started</a>
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

    @media only screen and (max-width: 735px) {
        .site-preview {
            display: none;
        }
    }

    @media only screen and (max-width: 735px) {
        .header {
            display: none;
        }
    }
</style>
