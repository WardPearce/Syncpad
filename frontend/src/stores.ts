import { get, set } from "idb-keyval";
import { get as storeGet, writable, type Writable } from "svelte/store";

export const advanceModeStore = writable(localStorage.getItem("advanceMode") === "true");
export const themeStore = writable({});

export const isDarkMode = writable(true);


export interface LocalSecretsModel {
    email: string,
    userId: string,
    jti: string,
    rawKeychain: string,
    rawKeypair: {
        publicKey: string,
        privateKey: string;
    };
}

export const emailVerificationRequired = writable(false);

async function getLocalSecrets(): Promise<LocalSecretsModel | undefined> {
    try {
        return await get("localSecrets");
    } catch {
        return undefined;
    }
}

export async function setLocalSecrets(secrets: LocalSecretsModel, indexDb: boolean = true) {
    if (indexDb) {
        try {
            // Catch if private tab.
            await set("localSecrets", secrets);
        } catch { }
    }
    localSecrets.set(secrets);
}


export const localSecrets: Writable<LocalSecretsModel | undefined> = writable(
    await getLocalSecrets()
);


export interface savedCanaryModel {
    id: string;
    publicKey: string;
}

export interface savedCanariesModel {
    [key: string]: savedCanaryModel;
}

export async function getSavedCanaries(): Promise<savedCanariesModel | undefined> {
    try {
        return await get("savedCanaries");
    } catch (error) {
        return undefined;
    }
}

export async function updateSavedCanaries(domain: string, canary: savedCanaryModel) {
    let oldCanaries;
    let toSave = {};
    try {
        oldCanaries = await get("savedCanaries");

        if (oldCanaries) {
            toSave = oldCanaries;
        }

        toSave[domain] = canary;
        await set("savedCanaries", toSave);
    } catch (error) { }

    if (oldCanaries === undefined) {
        oldCanaries = storeGet(savedCanaries);
        if (oldCanaries) {
            toSave = oldCanaries;
        }
        oldCanaries = { ...oldCanaries, domain: canary };
        toSave[domain] = canary;
    }

    savedCanaries.set(toSave);
}


export const savedCanaries: Writable<savedCanariesModel | undefined> = writable(
    await getSavedCanaries()
);
