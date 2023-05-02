<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-navigator";
  import { advanceModeStore, themeStore } from "../stores";
  import { get } from "svelte/store";
  import { getDynamicTheme } from "../lib/theme";

  export let isMobile: boolean = false;

  let mode = "dark";

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

<a use:link href="/login" class={isMobile ? "row round" : ""}>
  <i>login</i>
  <span>Login</span>
</a>
<a use:link href="/register" class={isMobile ? "row round" : ""}>
  <i>person_add_alt</i>
  <span>Register</span>
</a>
<a use:link href="/dashboard/add-site" class={isMobile ? "row round" : ""}>
  <i>add</i>
  <span>Add a site</span>
</a>
<a use:link href="/" class={isMobile ? "row round" : ""}>
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
    <input type="checkbox" on:click={onAdvanceModeToggle} />
    <span />
  </label>
  <p>Advance mode</p>
</div>
