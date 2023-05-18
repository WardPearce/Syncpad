import { writable, type Writable } from "svelte/store";
import { get, set } from "idb-keyval";

export const advanceModeStore = writable(false);
export const themeStore = writable({});


export interface LocalSecretsModel {
    email: string,
    userId: string,
    rawKeychain: Uint8Array,
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
