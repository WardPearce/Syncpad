import sodium from "libsodium-wrappers-sumo";
import { get } from "svelte/store";
import { localSecrets } from "../../stores";
import { base64Decode, base64Encode, utf8Decode, utf8Encode } from "./codecUtils";

export enum SecretkeyLocation {
  localKeychain = "localKeychain",
  generate = "generate"
}

export type Key = Uint8Array | SecretkeyLocation;

export interface encryptedData {
  cipherText: string;
  iv: string;
  rawSecretKey: Uint8Array;
}

export class KeychainUndefinedError extends Error {
  constructor() {
    super();
    this.message = "Keychain can not be undefined";
    this.name = "KeychainUndefinedError";
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
    const storedSecrets = get(localSecrets);
    if (typeof storedSecrets === "undefined" || !("rawKeychain" in storedSecrets) || !storedSecrets.rawKeychain) {
      throw new KeychainUndefinedError();
    }
    return base64Decode(storedSecrets.rawKeychain);
  } else {
    return generateKey();
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
    rawSecretKey: rawKey,
  };
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
};
