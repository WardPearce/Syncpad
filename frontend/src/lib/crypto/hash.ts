import sodium from "libsodium-wrappers-sumo";
import { base64Encode } from "./codecUtils";

export function hashBase64Encode(toHash: string | Uint8Array, urlSafe: boolean = false): string {
  return base64Encode(
    sodium.crypto_generichash(
      sodium.crypto_generichash_BYTES,
      toHash
    ),
    urlSafe
  );
}

export default {
  hashBase64Encode
};