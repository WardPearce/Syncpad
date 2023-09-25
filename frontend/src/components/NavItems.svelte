<script lang="ts">
  import { onMount } from "svelte";
  import { link, useLocation } from "svelte-navigator";
  import { get } from "svelte/store";

  import { logout } from "../lib/account";
  import { getDynamicTheme } from "../lib/theme";
  import {
    advanceModeStore,
    enabled,
    isDarkMode,
    localSecrets,
    themeStore,
    type LocalSecretsModel,
  } from "../stores";
  import Logo from "./Logo.svelte";

  export let isMobile: boolean = false;

  enum ThemeMode {
    dark = "dark",
    light = "light",
  }

  const enabledSettings = get(enabled);

  let mode: ThemeMode;

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
    mode = mode === ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    await window.ui("mode", mode);
    localStorage.setItem("mode", mode);

    isDarkMode.set(mode === ThemeMode.dark);
    themeStore.set(await getDynamicTheme(mode));
  }

  onMount(async () => {
    const localStorageMode = localStorage.getItem("mode");
    if (localStorageMode) {
      mode = localStorageMode as ThemeMode;
      await window.ui("mode", mode);
    } else if (
      window.matchMedia &&
      !window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      mode = ThemeMode.light;
      await window.ui("mode", mode);
    } else {
      mode = ThemeMode.dark;
      await window.ui("mode", mode);
    }

    isDarkMode.set(mode === ThemeMode.dark);

    themeStore.set(await getDynamicTheme());
  });
</script>

{#if !isMobile}
  <a href={loggedInUser === undefined ? "/" : "/dashboard"} use:link>
    <div class="logo">
      <Logo />
    </div>
  </a>
{/if}

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
{#if enabledSettings.canaries}
  <a
    use:link
    href="/canaries"
    class:active={currentPage === "/canaries"}
    class={isMobile ? "row round" : ""}
  >
    <i>bookmarks</i>
    <span>Trusted Canaries</span>
  </a>
{/if}
<a
  target="_blank"
  referrerpolicy="no-referrer"
  href="https://github.com/WardPearce/Purplix.io"
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
    <input
      type="checkbox"
      checked={mode === ThemeMode.dark}
      on:click={toggleMode}
    />
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
  <p>Advanced mode</p>
</div>
