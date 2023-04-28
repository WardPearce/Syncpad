import App from "./App.svelte"
import "./assets/styles.css"

import "beercss";
import "material-dynamic-colors";

const app = new App({
  target: document.getElementById("app"),
})

export default app
