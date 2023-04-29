<script lang="ts">
  import { onMount } from "svelte";
  import { Router, link, Route } from "svelte-navigator";
  import LazyRoute from "./components/LazyRoute.svelte";
  import PageLoading from "./components/PageLoading.svelte";
  import { advanceModeStore, themeStore } from "./stores";
  import { get } from "svelte/store";
  import { getDynamicTheme } from "./lib/theme";

  const CanaryLoader = () => import("./routes/Canary.svelte");
  const LoginLoader = () => import("./routes/Login/Login.svelte");
  const DashboardLoader = () => import("./routes/Dashboard/Dashboard.svelte");

  let mode = "dark";
  let mobileNavShow = false;

  function onAdvanceModeToggle() {
    advanceModeStore.set(!get(advanceModeStore));
  }

  async function toggleMode() {
    mode = mode === "dark" ? "light" : "dark";
    await window.ui("mode", mode);
    localStorage.setItem("mode", mode);
    themeStore.set(await getDynamicTheme(mode));
  }

  onMount(async () => {
    const localStorageMode = localStorage.getItem("mode");
    if (localStorageMode) {
      mode = localStorageMode;
      await window.ui("mode", mode);
    } else if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      await window.ui("mode", "dark");
    }

    themeStore.set(await getDynamicTheme());
  });
</script>

<Router primary={false}>
  <!-- Stupid repetitive nav code, should be cleaned up -->
  <header class="mobile-nav">
    <nav>
      <button
        class="circle transparent"
        on:click={() => (mobileNavShow = true)}
      >
        <i>menu</i>
      </button>
    </nav>
  </header>

  <div class={`modal left ${mobileNavShow ? "active" : ""}`}>
    <header class="fixed">
      <nav>
        <button
          class="transparent circle large"
          on:click={() => (mobileNavShow = false)}
        >
          <i>close</i>
        </button>
        <h5 class="max">Canary Status</h5>
      </nav>
    </header>
    <a use:link href="/login" class="row round">
      <i>login</i>
      <span>Login</span>
    </a>
    <a href="/" class="row round">
      <i>add</i>
      <span>Add a site</span>
    </a>
    <a href="/" class="row round">
      <i>article</i>
      <span>About</span>
    </a>
    <a
      target="_blank"
      referrerpolicy="no-referrer"
      href="https://github.com/WardPearce/canarystatus.com"
      class="row round"
    >
      <i>code</i>
      <span>Github</span>
    </a>
    <div class="row round">
      <label class="switch icon">
        <input
          type="checkbox"
          checked={mode === "dark"}
          on:click={toggleMode}
        />
        <span>
          <i>{`${mode}_mode`}</i>
        </span>
      </label>
      <p><span style="text-transform: capitalize;">{mode}</span> mode</p>
    </div>

    <div class="row round">
      <label class="switch">
        <input type="checkbox" on:click={onAdvanceModeToggle} />
        <span />
      </label>
      <p>Advance mode</p>
    </div>
  </div>

  <nav class="m l right">
    <a use:link href="/login">
      <i>login</i>
      <span>Login</span>
    </a>
    <a href="/">
      <i>add</i>
      <span>Add a site</span>
    </a>
    <a href="/">
      <i>article</i>
      <span>About</span>
    </a>
    <a
      target="_blank"
      referrerpolicy="no-referrer"
      href="https://github.com/WardPearce/canarystatus.com"
    >
      <i>code</i>
      <span>Github</span>
    </a>
    <div>
      <label class="switch icon">
        <input
          type="checkbox"
          checked={mode === "dark"}
          on:click={toggleMode}
        />
        <span>
          <i>{`${mode}_mode`}</i>
        </span>
      </label>
      <p><span style="text-transform: capitalize;">{mode}</span> mode</p>
    </div>

    <div>
      <label class="switch">
        <input type="checkbox" on:click={onAdvanceModeToggle} />
        <span />
      </label>
      <p>Advance mode</p>
    </div>
  </nav>

  <main class="responsive">
    <Route path="/">
      <PageLoading />
    </Route>
    <LazyRoute path="/login" component={LoginLoader}>
      <PageLoading />
    </LazyRoute>
    <LazyRoute path="/dashboard" component={DashboardLoader}>
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/register"
      componentProps={{ isRegister: true }}
      component={LoginLoader}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute path="/:domainName" component={CanaryLoader}>
      <PageLoading />
    </LazyRoute>
  </main>
</Router>

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
