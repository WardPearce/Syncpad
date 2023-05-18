<script lang="ts">
  export let domainName: string;

  let verifyCode = "canary=t6V4NtZmaWD4Mt";
</script>

<h4>Verify domain</h4>
<h6>Step 1</h6>
<p>Log in to your DNS provider's control panel or dashboard.</p>

<h6>Step 2</h6>
<p>
  Look for the option to add a new DNS record and select "TXT" as the record
  type.
</p>
<p>
  In the "Name" or "Host" field, enter "@" or leave it blank to create the TXT
  record for the domain itself.
</p>

<h6>Step 3</h6>
<p>In the "Value" or "Data" field, enter the following.</p>

<nav>
  <div class="field border">
    <input type="text" disabled value={verifyCode} />
  </div>
  <button
    class="square"
    on:click={async () => {
      await navigator.clipboard.writeText(verifyCode);
    }}
  >
    <i>content_copy</i>
  </button>
</nav>

<h6>Step 4</h6>
<p>
  Please wait for DNS propagation to occur, which can take anywhere from a few
  minutes to several hours.
</p>
<p>
  {import.meta.env.VITE_SITE_NAME} will check automatically every so often. Expect
  an email once validation is successful.
</p>

<div class="right-align" style="margin-top: 1em;">
  <button>
    <i>travel_explore</i>
    <span>Validate domain</span>
  </button>
</div>
