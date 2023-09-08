<script>
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
    let roller;

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
            <a use:link href="/register" class="chip fill">Register</a>
            <a use:link href="/login" class="chip">Login</a>
        </div>
    </nav>
</article>

<div class="header">
    {#key wordsIndex}
        <h2>
            Securely survey your&nbsp;<span
                in:slide
                out:slide={{ duration: 0 }}
                style="font-weight: bolder;">{words[wordsIndex]}</span
            >
        </h2>
        <h6>
            Only&nbsp;<span style="font-weight: bolder;">you</span>&nbsp;can see
            the results, not us, not the government.
        </h6>
    {/key}
</div>

<article>
    <h3>Surveys</h3>
    <p>ToDO: About surveys here</p>
    <h3>Canaries</h3>
    <p>ToDO: About canaries here</p>
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
    }

    .header h6,
    .header h2 {
        margin-top: 0.3em;
        margin-bottom: 0;
    }
</style>
