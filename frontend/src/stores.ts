import * as idbKeyval from "idb-keyval";
import { writable, type Writable } from "svelte/store";

export const advanceModeStore = writable(localStorage.getItem("advanceMode") === "true");
export const themeStore: Writable<Record<string, string>> = writable({});

export const isDarkMode = writable(true);

export const showNav = writable(true);

export const enabled: Writable<{
    canaries: boolean;
    survey: boolean;
}> = writable({ canaries: true, survey: true });

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


export interface savedCanariesModel {
    [key: string]: string;
}

async function indexDbCanaries(): Promise<savedCanariesModel> {
    try {
        const local = await idbKeyval.get("savedCanaries");
        if (local) {
            return local;
        }
    } catch (error) { }
    return {};
}


export const savedCanaries: Writable<savedCanariesModel> = writable(
    await indexDbCanaries()
);
