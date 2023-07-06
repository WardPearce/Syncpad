import sodium from "libsodium-wrappers-sumo";
import { get } from "svelte/store";
import { localSecrets } from "../../stores";
import { base64Decode, utf8Decode } from "./codecUtils";

export enum PublicKeyLocation {
  localKeypair = "localPublicKeypair"
}

export enum PrivateKeyLocation {
  localKeypair = "localPrivateKeypair"
}

export type PublicKey = Uint8Array | PublicKeyLocation | string;
export type PrivateKey = Uint8Array | PrivateKeyLocation;

export interface KeyPair {
  publicKey: PublicKey;
  privateKey: PrivateKey;
}

export class KeypairUndefinedError extends Error {
  constructor() {
    super();
    this.message = "Keypair can not be undefined";
    this.name = "KeypairUndefinedError";
  }
}

export function determineKeyLocation(key: PublicKey | PrivateKey): Uint8Array {
  if (key instanceof Uint8Array) {
    return key;
  } else if (key === PublicKeyLocation.localKeypair || key === PrivateKeyLocation.localKeypair) {
    const storedSecrets = get(localSecrets);
    const keypairKey = key === PrivateKeyLocation.localKeypair ? "privateKey" : "publicKey";
    if (typeof storedSecrets === "undefined" || !("rawKeypair" in storedSecrets) || !(keypairKey in storedSecrets["rawKeypair"])) {
      throw new KeypairUndefinedError();
    }
    return base64Decode(storedSecrets.rawKeypair[keypairKey]);
  } else {
    return base64Decode(key);
  }
}

export function generateKeypair(): sodium.KeyPair {
  return sodium.crypto_box_keypair();
}

export function boxSealOpen(
  publicKey: PublicKey,
  privateKey: PrivateKey,
  toDecrypt: string, utf8: boolean = false
): string | Uint8Array {

  const rawData = sodium.crypto_box_seal_open(
    base64Decode(toDecrypt),
    determineKeyLocation(publicKey),
    determineKeyLocation(privateKey)
  );

  return utf8 ? utf8Decode(rawData) : rawData;
}

export default {
  generateKeypair,
  boxSealOpen
};
