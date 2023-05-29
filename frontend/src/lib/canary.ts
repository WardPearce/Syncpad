import * as idbKeyval from "idb-keyval";
import sodium from "libsodium-wrappers-sumo";
import { navigate } from 'svelte-navigator';
import { get } from "svelte/store";

import { localSecrets, savedCanaries } from "../stores";
import apiClient from "./apiClient";
import { type CanaryModel } from './client/models/CanaryModel';
import { hashBase64Encode } from './crypto/hash';
import secretKey, { SecretkeyLocation } from './crypto/secretKey';
import signatures, { SignatureKeyLocation } from "./crypto/signatures";


export function goToCanary(canary: CanaryModel): void {
  // Allows us to validate the public key when
  // the canary owner wants to visit their canary off the dashboard.
  const canaryPrivateKey = secretKey.decrypt(
    SecretkeyLocation.localKeychain,
    canary.keypair.iv,
    canary.keypair.cipher_text
  );

  const canaryPublicKey = sodium.crypto_sign_ed25519_sk_to_pk(
    canaryPrivateKey as Uint8Array
  );

  const hash = hashBase64Encode(canaryPublicKey, true);
  navigate(`/c/${canary.domain}/${hash}`, { replace: true });
}

export async function getTrustedCanary(domain: string): Promise<string | void> {
  const canaries = get(savedCanaries);
  if (domain in canaries) {
    return canaries[domain];
  } else if (get(localSecrets) !== undefined) {
    try {
      const untrusted = await apiClient.canary.controllersCanaryDomainTrustedGetTrusted(domain);

      const trustedData = JSON.parse(
        signatures.open(
          SignatureKeyLocation.localPublicSignKeypair,
          untrusted.signature,
          true
        ) as string
      );

      if (domain !== trustedData.domain) {
        return;
      } else {
        return trustedData.public_key_hash;
      }
    } catch { }
  }
}

export async function listTrustedCanaries(): Promise<Record<string, string>> {
  const canaries = get(savedCanaries);
  if (Object.keys(canaries).length > 0) {
    return canaries;
  } else if (get(localSecrets) !== undefined) {
    try {
      const untrustedCanaries = await apiClient.canary.controllersCanaryTrustedListListTrustedCanaries();

      const trustedCanaries = {};
      untrustedCanaries.forEach(untrustedCanary => {
        try {
          const trustedData = JSON.parse(
            signatures.open(
              SignatureKeyLocation.localPublicSignKeypair,
              untrustedCanary.signature,
              true
            ) as string
          );
          trustedCanaries[trustedData.domain] = trustedData.public_key_hash;
        } catch { }
      });

      return trustedCanaries;
    } catch { }
  }

  return {};
}

export async function saveCanaryAsTrusted(domain: string, publicKeyHash: string) {
  let oldCanaries = get(savedCanaries);
  oldCanaries[domain] = publicKeyHash;

  savedCanaries.set(oldCanaries);

  if (get(localSecrets) !== undefined) {
    // Update signed hash in the background
    apiClient.canary.controllersCanaryDomainTrustedAddTrustCanary(
      domain,
      {
        signature: signatures.sign(
          SignatureKeyLocation.localPrivateSignKeypair,
          JSON.stringify({
            "domain": domain,
            "public_key_hash": publicKeyHash
          })
        )
      }
    );
  }

  try {
    await idbKeyval.set("savedCanaries", oldCanaries);
  } catch { }
}

export default {
  goToCanary,
  getTrustedCanary,
  saveCanaryAsTrusted,
  listTrustedCanaries
};
