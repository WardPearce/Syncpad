import { writable, type Writable } from "svelte/store";
import { get, set } from "idb-keyval";

export const advanceModeStore = writable(localStorage.getItem("advanceMode") === "true");
export const themeStore = writable({});


export interface LocalSecretsModel {
    email: string,
    userId: string,
    jti: string,
    rawKeychain: string,
    rawKeypair: {
        publicKey: string,
        privateKey: string
    }
}

export const emailVerificationRequired = writable(false);

async function getLocalSecrets(): Promise<LocalSecretsModel | undefined> {
    try {
        return await get("localSecrets")
    } catch {
        return undefined
    }
}

export const localSecrets: Writable<LocalSecretsModel | undefined> = writable(
    await getLocalSecrets()
);


export async function setLocalSecrets(secrets: LocalSecretsModel) {
    try {
        // Catch if private tab.
        await set("localSecrets", secrets);
    } catch { }
    localSecrets.set(secrets);
}
