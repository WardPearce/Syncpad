<script lang="ts">
  import { onMount } from "svelte";
  import { link, Router } from "svelte-navigator";

  import sodium from "libsodium-wrappers-sumo";

  import LazyRoute from "./components/LazyRoute.svelte";
  import NavItems from "./components/NavItems.svelte";
  import PageLoading from "./components/PageLoading.svelte";

  import account from "./lib/account";
  import apiClient from "./lib/apiClient";

  import Logo from "./components/Logo.svelte";
  import {
    emailVerificationRequired,
    isDarkMode,
    localSecrets,
    type LocalSecretsModel,
  } from "./stores";

  let mobileNavShow = false;

  let loggedInUser: LocalSecretsModel | undefined;
  localSecrets.subscribe((secrets) => (loggedInUser = secrets));

  let darkMode: boolean;
  isDarkMode.subscribe((isDark) => (darkMode = isDark));

  let emailVerification: boolean;
  emailVerificationRequired.subscribe(
    (required) => (emailVerification = required)
  );

  let emailResent = false;
  async function resendEmail() {
    emailResent = true;
    await apiClient.account.controllersAccountEmailResendEmailResend();
    emailResent = false;
  }

  onMount(async () => {
    // Default UI color
    await ui("theme", import.meta.env.VITE_THEME);
    document.title = import.meta.env.VITE_SITE_NAME;

    await sodium.ready;

    if (loggedInUser === undefined) {
      return;
    }

    // Validate JWT session.
    try {
      const userId = await apiClient.account.controllersAccountJwtJwtInfo();
      if (userId !== loggedInUser.userId) {
        await account.logout();
      }
    } catch (error) {
      await account.logout();
    }
  });
</script>

<Router primary={false}>
  <header class="mobile-nav" class:surface-variant={!darkMode}>
    <nav>
      <button
        class="circle transparent"
        on:click={() => (mobileNavShow = true)}
      >
        <i>menu</i>
      </button>
    </nav>
  </header>

  <dialog
    class="modal left"
    class:active={mobileNavShow}
    class:surface-variant={!darkMode}
  >
    <header class="fixed">
      <nav style="display: flex;justify-content: space-between;">
        <a href={loggedInUser === undefined ? "/" : "/dashboard"} use:link>
          <div class="logo">
            <Logo />
          </div>
        </a>
        <button
          class="transparent circle large"
          on:click={() => (mobileNavShow = false)}
        >
          <i>close</i>
        </button>
      </nav>
    </header>
    <NavItems isMobile={true} />
  </dialog>

  <nav class="m l left" class:surface-variant={!darkMode}>
    <NavItems isMobile={false} />
  </nav>

  <main class="responsive">
    {#if emailVerification}
      <article style="margin-bottom: 2em;">
        <nav>
          <h6>Please verify your email.</h6>
          {#if !emailResent}
            <button class="extend square round small" on:click={resendEmail}>
              <i>loop</i>
              <span>Resend email</span>
            </button>
          {:else}
            <span class="loader small" />
          {/if}
        </nav>
        <p>
          {import.meta.env.VITE_SITE_NAME} has sent you a verification email, please
          check your spam.
        </p>
      </article>
    {/if}
    <LazyRoute path="/" component={() => import("./routes/About.svelte")}>
      <PageLoading />
    </LazyRoute>
    <LazyRoute path="/login" component={() => import("./routes/Login.svelte")}>
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard"
      component={() => import("./routes/Dashboard/Dashboard.svelte")}
      requiresAuth={true}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/survey/create"
      component={() => import("./routes/Dashboard/Survey/Create.svelte")}
      requiresAuth={true}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/canary/add-site"
      component={() => import("./routes/Dashboard/Canary/AddSite.svelte")}
      requiresAuth={true}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/canary/verify-site/:domainName"
      component={() => import("./routes/Dashboard/Canary/VerifySite.svelte")}
      requiresAuth={true}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/canary/publish/:domainName"
      component={() => import("./routes/Dashboard/Canary/Publish.svelte")}
      requiresAuth={true}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/email-verified"
      component={() => import("./routes/EmailVerified.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/register"
      componentProps={{ isRegister: true }}
      component={() => import("./routes/Login.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/account"
      requiresAuth={true}
      component={() => import("./routes/Account.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/canaries"
      component={() => import("./routes/SavedCanaries.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/s/:surveyId/:signPublicKeyHash"
      component={() => import("./routes/Survey.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/c/:domainName/:signPublicKeyHash"
      component={() => import("./routes/Canary.svelte")}
    >
      <PageLoading />
    </LazyRoute>
  </main>
</Router>

<footer class:surface-variant={!darkMode}>
  <nav class="center-align">
    <a use:link href="/privacy-policy" class="link">
      <i>policy</i>
      <span>Privacy Policy</span>
    </a>
    <a use:link href="/terms-of-service" class="link">
      <i>gavel</i>
      <span>Terms of Service</span>
    </a>
  </nav>
</footer>

<style>
  .mobile-nav {
    display: none;
  }

  @media only screen and (max-width: 600px) {
    .mobile-nav {
      display: block;
    }
  }
</style>
