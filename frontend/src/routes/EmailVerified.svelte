<script lang="ts">
  import { onMount } from "svelte";
  import { navigate } from "svelte-navigator";
  import CheckMark from "../components/CheckMark.svelte";

  onMount(() => {
    setTimeout(() => navigate("/dashboard"), 10000);
  });
</script>

<CheckMark header="Email verification completed!" />
