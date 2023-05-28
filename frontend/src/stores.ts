import * as idbKeyval from "idb-keyval";
import { get, writable, type Writable } from "svelte/store";

export const advanceModeStore = writable(localStorage.getItem("advanceMode") === "true");
export const themeStore = writable({});

export const isDarkMode = writable(true);


export interface LocalSecretsModel {
    email: string;
    userId: string;
    jti: string;
    rawKeychain: string;
    rawKeypair: {
        publicKey: string;
        privateKey: string;
    };
    rawSignKeypair: {
        publicKey: string;
        privateKey: string;
    };
}

export const emailVerificationRequired = writable(false);

async function indexDbLocalSecrets(): Promise<LocalSecretsModel | undefined> {
    try {
        return await idbKeyval.get("localSecrets");
    } catch {
        return undefined;
    }
}

export async function setLocalSecrets(secrets: LocalSecretsModel, indexDb: boolean = true) {
    if (indexDb) {
        try {
            // Catch if private tab.
            await idbKeyval.set("localSecrets", secrets);
        } catch { }
    }
    localSecrets.set(secrets);
}


export const localSecrets: Writable<LocalSecretsModel | undefined> = writable(
    await indexDbLocalSecrets()
);


export interface savedCanaryModel {
    id: string;
    publicKey: string;
}

export interface savedCanariesModel {
    [key: string]: savedCanaryModel;
}

async function indexDbCanaries(): Promise<savedCanariesModel | undefined> {
    try {
        return await idbKeyval.get("savedCanaries");
    } catch (error) {
        return undefined;
    }
}

export async function updateSavedCanaries(domain: string, canary: savedCanaryModel) {
    let oldCanaries;
    let toSave = {};
    try {
        oldCanaries = await idbKeyval.get("savedCanaries");

        if (oldCanaries) {
            toSave = oldCanaries;
        }

        toSave[domain] = canary;
        await idbKeyval.set("savedCanaries", toSave);
    } catch (error) { }

    if (oldCanaries === undefined) {
        oldCanaries = get(savedCanaries);
        if (oldCanaries) {
            toSave = oldCanaries;
        }
        oldCanaries = { ...oldCanaries, domain: canary };
        toSave[domain] = canary;
    }

    savedCanaries.set(toSave);
}


export const savedCanaries: Writable<savedCanariesModel | undefined> = writable(
    await indexDbCanaries()
);
