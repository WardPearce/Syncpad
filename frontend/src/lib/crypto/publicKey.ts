
export enum PublickeyLocation {
    localPublic = "localPublic",
    generate = "generate"
}

export enum PrivateKeyLocation {
    localPrivate = "localPrivate",
    generate = "generate"
}

export type PublicKey = Uint8Array | string | PublickeyLocation;
export type PrivateKey = Uint8Array | string | PrivateKeyLocation;

