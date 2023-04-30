<script lang="ts">
  import { link } from "svelte-navigator";
  import ColorPicker, { ChromeVariant } from "svelte-awesome-color-picker";

  let hex;

  async function onColorChange() {
    await window.ui("theme", hex);
  }
</script>

<h4>Add site</h4>
<div class="field label border">
  <input type="text" />
  <label for="domain">Domain name</label>
  <span class="helper">0/200</span>
</div>

<div class="field textarea label border">
  <textarea />
  <label for="about">About your site</label>
  <span class="helper">0/500</span>
</div>

<nav>
  <div class="field label suffix border">
    <input type="text" />
    <input type="file" />
    <label for="logo">Logo</label>
    <i>attach_file</i>
    <span class="helper">Max 5MB - PNG, GIF, JPEG</span>
  </div>

  <ColorPicker
    bind:hex
    label="Theme color"
    canChangeMode={false}
    isAlpha={false}
    components={ChromeVariant}
    toRight={true}
    on:input={onColorChange}
  />
</nav>

<div class="right-align">
  <a class="button" href="/dashboard/verify-site/123" use:link>
    <i>arrow_forward_ios</i>
    <span>Next step</span>
  </a>
</div>
