<script lang="ts">
  import { Router, Route } from "svelte-navigator";
  import { onMount } from "svelte";

  import LazyRoute from "./components/LazyRoute.svelte";
  import PageLoading from "./components/PageLoading.svelte";
  import NavItems from "./components/NavItems.svelte";

  import { client } from "./lib/canary";
  import { logout } from "./lib/logout";
  import { localSecrets, type LocalSecretsModel } from "./stores";

  let mobileNavShow = false;

  let loggedInUser: LocalSecretsModel | undefined;
  localSecrets.subscribe((secrets) => (loggedInUser = secrets));

  onMount(async () => {
    // Validate JWT session.
    try {
      const userId = await client.account.controllersAccountMeMe();
      if (userId !== loggedInUser.userId) {
        await logout();
      }
    } catch (error) {
      await logout();
    }
  });
</script>

<Router primary={false}>
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
        <h6 class="max">Canary status</h6>
      </nav>
    </header>
    <NavItems isMobile={true} />
  </div>

  <nav class="m l right">
    <NavItems isMobile={false} />
  </nav>

  <main class="responsive">
    <Route path="/">
      <PageLoading />
    </Route>
    <LazyRoute path="/login" component={() => import("./routes/Login.svelte")}>
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard"
      component={() => import("./routes/Dashboard/Dashboard.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/add-site"
      component={() => import("./routes/Dashboard/AddSite.svelte")}
    >
      <PageLoading />
    </LazyRoute>
    <LazyRoute
      path="/dashboard/verify-site/:domainName"
      component={() => import("./routes/Dashboard/VerifySite.svelte")}
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
      path="/:domainName"
      component={() => import("./routes/Canary.svelte")}
    >
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
