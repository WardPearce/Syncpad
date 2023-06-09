import App from "./App.svelte";

import "beercss";
import "material-dynamic-colors";

import "./assets/styles.css";

const app = new App({
  target: document.getElementById("app") as HTMLElement,
});

export default app;
