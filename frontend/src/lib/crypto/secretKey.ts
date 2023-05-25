import sodium from "libsodium-wrappers-sumo";
import { base64Decode, base64Encode, utf8Decode, utf8Encode } from "./codecUtils";
import { get } from "svelte/store";
import { localSecrets } from "../../stores";

export enum SecretkeyLocation {
    localKeychain = "localKeychain",
    generate = "generate"
}

export type Key = Uint8Array | string | SecretkeyLocation;

export interface encryptedData {
  cipherText: string
  iv: string,
  key: string
}

export class KeychainUndefinedError extends Error {
  constructor() {
    super();
    this.message = "Keychain can not be undefined";
    this.name = "KeychainUndefinedError"
  }
}

export function generateIv(): Uint8Array {
  return sodium.randombytes_buf(sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES);
}

export function generateKey(): Uint8Array {
  return sodium.crypto_aead_xchacha20poly1305_ietf_keygen();
}

export function determineKeyLocation(key: Key): Uint8Array {
  if (key instanceof Uint8Array) {
    return key;
  } else if (key === SecretkeyLocation.localKeychain) {
    const keychain = get(localSecrets).rawKeychain;
    if (typeof keychain === "undefined") {
        throw new KeychainUndefinedError();
    }
  } else if (key === SecretkeyLocation.generate) {
    return generateKey();
  } else {
    return base64Decode(key);
  }
}

export function encrypt(
    key: Key,
    toEncrypt: Uint8Array | string,
): encryptedData {
  const rawKey = determineKeyLocation(key);
  const rawIv = generateIv();

  const cipher = sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
    toEncrypt instanceof Uint8Array ? toEncrypt : utf8Encode(toEncrypt),
    null,
    null,
    rawIv,
    rawKey,
  );

  return {
    cipherText: base64Encode(cipher),
    iv: base64Encode(rawIv),
    key: base64Encode(key)
  }
}

export function decrypt(
    key: Key,
    iv: string,
    toDecrypt: string,
    utf8: boolean = false
): Uint8Array | string {
  const rawKey = determineKeyLocation(key);

  const rawData = sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
    null,
    base64Decode(toDecrypt),
    null,
    base64Decode(iv),
    rawKey
  );

  return utf8 ? utf8Decode(rawData) : rawData;
}

export default {
  encrypt,
  decrypt,
  generateIv,
  generateKey
}
