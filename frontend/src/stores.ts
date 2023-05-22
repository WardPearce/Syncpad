import { writable, type Writable } from "svelte/store";
import { get, set } from "idb-keyval";

export const advanceModeStore = writable(localStorage.getItem("advanceMode") === "true");
export const themeStore = writable({});


export interface LocalSecretsModel {
    email: string,
    userId: string,
    jti: string,
    rawKeychain: string,
    rawKeypairPrivateKey: string
}

export const localSecrets: Writable<LocalSecretsModel | undefined> = writable(
    await get("localSecrets")
);


export async function setLocalSecrets(secrets: LocalSecretsModel) {
    try {
        // Catch if private tab.
        await set("localSecrets", secrets);
    } catch { }
    localSecrets.set(secrets);
}
