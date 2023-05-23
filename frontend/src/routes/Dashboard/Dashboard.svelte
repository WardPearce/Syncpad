<script lang="ts">
  import { link } from "svelte-navigator";
  import { concat } from "../../lib/misc";
</script>

<h3>My surveys</h3>
<p>placeholder</p>

<h3>Canaries</h3>
<div class="grid">
  <div class="s12 m6 l4">
    <article>
      <div class="row">
        <img
          class="small"
          src="https://www.privacyguides.org/en/assets/brand/SVG/Logo/privacy-guides-logo-notext-darkbg.svg#only-dark"
        />
        <div class="max">
          <a href="/privacyguides.org" use:link class="link">
            <h6>{concat("privacyguides.org")}</h6>
          </a>
        </div>
      </div>
      <nav>
        <button>Update Canary</button>
        <button class="border">Edit</button>
      </nav>
    </article>
  </div>
  <div class="s12 m6 l4">
    <article class="border center-align middle-align" style="height: 100%;">
      <a class="button" href="/dashboard/add-site" use:link>
        <i>add</i>
        <span>Add site</span>
      </a>
    </article>
  </div>
</div>
