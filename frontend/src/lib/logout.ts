import { del } from "idb-keyval";
import { client } from "../lib/canary";
import { localSecrets } from "../stores";
import {  navigate } from "svelte-navigator";

export async function logout() {
    try {
        await client.account.controllersAccountLogoutLogout();
    } catch {}
    try {
        await del("localSecrets");
    } catch {}
    localSecrets.set(undefined);
    navigate("/", { replace: true });
}
