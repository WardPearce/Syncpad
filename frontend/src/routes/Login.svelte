<script lang="ts">
  import { link } from "svelte-navigator";

  export let isRegister = false;

  let mode = isRegister ? "Register" : "Login";
</script>

<main>
  <article>
    <h5>{mode}</h5>
    {#if !isRegister}
      <a href="/register" use:link class="link"
        >Need a account? Register here.</a
      >
    {:else}
      <a href="/login" use:link class="link">Already have an account? Login.</a>
    {/if}

    <form>
      <div class="field label border medium-divider fill">
        <input type="text" />
        <label for="email">Email</label>
      </div>
      <div class="field label border medium-divider fill">
        <input type="password" />
        <label for="password">Password</label>
      </div>
      {#if isRegister}
        <div class="field label border medium-divider fill">
          <input type="password" />
          <label for="password">Repeat Password</label>
        </div>
      {/if}
      <label class="checkbox">
        <input type="checkbox" />
        <span>Remember me</span>
      </label>

      <div class="right-align" style="margin-top: 1em;">
        <button type="submit">
          <i>login</i>
          <span>{mode}</span>
        </button>
      </div>
    </form>
  </article>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>
