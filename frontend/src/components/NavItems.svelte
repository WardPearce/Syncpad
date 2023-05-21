<script lang="ts">
  import { onMount } from "svelte";
  import { link, useLocation } from "svelte-navigator";
  import {
    advanceModeStore,
    themeStore,
    localSecrets,
    type LocalSecretsModel,
  } from "../stores";
  import { get } from "svelte/store";
  import { getDynamicTheme } from "../lib/theme";
  import { logout } from "../lib/logout";

  export let isMobile: boolean = false;

  let mode: string;

  let isAdvanceMode: boolean;
  advanceModeStore.subscribe((status) => (isAdvanceMode = status));

  let loggedInUser: LocalSecretsModel | undefined;
  localSecrets.subscribe((secrets) => (loggedInUser = secrets));

  let currentPage: string;
  useLocation().subscribe((page) => (currentPage = page.pathname));

  function onAdvanceModeToggle() {
    const advanceModeToggled = !get(advanceModeStore);

    advanceModeStore.set(advanceModeToggled);

    if (advanceModeToggled) {
      localStorage.setItem("advanceMode", "true");
    } else {
      localStorage.removeItem("advanceMode");
    }
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
      !window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      mode = "light";
      await window.ui("mode", mode);
    } else {
      mode = "dark";
      await window.ui("mode", mode);
    }

    themeStore.set(await getDynamicTheme());
  });
</script>

{#if loggedInUser === undefined}
  <a
    use:link
    href="/login"
    class:active={currentPage === "/login"}
    class={isMobile ? "row round" : ""}
  >
    <i>login</i>
    <span>Login</span>
  </a>
  <a
    use:link
    href="/register"
    class:active={currentPage === "/register"}
    class={isMobile ? "row round" : ""}
  >
    <i>person_add_alt</i>
    <span>Register</span>
  </a>
{:else}
  <a
    use:link
    href="/dashboard"
    class:active={currentPage === "/dashboard"}
    class={isMobile ? "row round" : ""}
  >
    <i>dashboard</i>
    <span>Dashboard</span>
  </a>
{/if}
<a
  use:link
  href="/dashboard/add-site"
  class:active={currentPage === "/dashboard/add-site"}
  class={isMobile ? "row round" : ""}
>
  <i>add</i>
  <span>Add a site</span>
</a>
{#if loggedInUser !== undefined}
  <a
    use:link
    href="/account"
    class:active={currentPage === "/account"}
    class={isMobile ? "row round" : ""}
  >
    <i>admin_panel_settings</i>
    <span>Account</span>
  </a>
{/if}
<a
  use:link
  href="/"
  class:active={currentPage === "/"}
  class={isMobile ? "row round" : ""}
>
  <i>article</i>
  <span>About</span>
</a>
<a
  target="_blank"
  referrerpolicy="no-referrer"
  href="https://github.com/WardPearce/canarystatus.com"
  class={isMobile ? "row round" : ""}
>
  <i>code</i>
  <span>Github</span>
</a>

{#if loggedInUser !== undefined}
  <a href="#logout" on:click={logout} class={isMobile ? "row round" : ""}>
    <i>logout</i>
    <span>Logout</span>
  </a>
{/if}

<div class={isMobile ? "row round" : ""}>
  <label class="switch icon">
    <input type="checkbox" checked={mode === "dark"} on:click={toggleMode} />
    <span>
      <i>{`${mode}_mode`}</i>
    </span>
  </label>
  <p><span style="text-transform: capitalize;">{mode}</span> mode</p>
</div>

<div class={isMobile ? "row round" : ""}>
  <label class="switch">
    <input
      type="checkbox"
      on:click={onAdvanceModeToggle}
      bind:checked={isAdvanceMode}
    />
    <span />
  </label>
  <p>Advance mode</p>
</div>
