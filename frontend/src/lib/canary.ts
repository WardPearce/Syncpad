import * as idbKeyval from "idb-keyval";
import sodium from "libsodium-wrappers-sumo";
import { navigate } from 'svelte-navigator';
import { get } from "svelte/store";

import { localSecrets, savedCanaries } from "../stores";
import apiClient from "./apiClient";
import { type CanaryModel } from './client/models/CanaryModel';
import { hashBase64Encode } from './crypto/hash';
import secretKey, { SecretkeyLocation } from './crypto/secretKey';
import signatures, { SignaturePrivateKeyLocation, SignaturePublicKeyLocation } from "./crypto/signatures";


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
  navigate(`/c/${canary.domain}/${hash}`);
}

export async function getTrustedCanary(domain: string): Promise<string | void> {
  const canaries = get(savedCanaries);
  if (domain in canaries) {
    return canaries[domain];
  } else if (get(localSecrets) !== undefined) {
    try {
      const untrusted = await apiClient.canary.controllersCanaryDomainTrustedGetTrusted(domain);

      signatures.validateHash(
        SignaturePublicKeyLocation.localKeypair,
        untrusted.signature,
        JSON.stringify({
          "domain": domain,
          "public_key_hash": untrusted.public_key_hash
        })
      );

      return untrusted.public_key_hash;
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
      for (const [domain, canary] of Object.entries(untrustedCanaries)) {
        try {
          signatures.validateHash(
            SignaturePublicKeyLocation.localKeypair,
            canary.signature,
            JSON.stringify({
              "domain": domain,
              "public_key_hash": canary.public_key_hash
            })
          );

          trustedCanaries[domain] = canary.public_key_hash;
        } catch { }
      }
      return trustedCanaries;
    } catch { }
  }

  return {};
}

export async function syncTrustedCanaries() {
  if (get(localSecrets) === undefined) {
    return;
  }

  const accountSavedCanaries = await apiClient.canary.controllersCanaryTrustedListListTrustedCanaries();
  const localSavedCanaries = get(savedCanaries);

  for (const [domain, publicKeyHash] of Object.entries(localSavedCanaries)) {
    if (!(domain in accountSavedCanaries)) {
      apiClient.canary.controllersCanaryDomainTrustedAddTrustCanary(
        domain,
        {
          public_key_hash: publicKeyHash,
          signature: signatures.signHash(
            SignaturePrivateKeyLocation.localKeypair,
            JSON.stringify({
              "domain": domain,
              "public_key_hash": publicKeyHash
            })
          )
        }
      );
    }
  }

  for (const [domain, canary] of Object.entries(accountSavedCanaries)) {
    if (!(domain in localSavedCanaries)) {
      try {
        signatures.validateHash(
          SignaturePublicKeyLocation.localKeypair,
          canary.signature,
          JSON.stringify({
            "domain": domain,
            "public_key_hash": canary.public_key_hash
          })
        );

        localSavedCanaries[domain] = canary.public_key_hash;
      } catch { }
    }
  }

  savedCanaries.set(localSavedCanaries);

  try {
    await idbKeyval.set("savedCanaries", localSavedCanaries);
  } catch { }
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
        public_key_hash: publicKeyHash,
        signature: signatures.signHash(
          SignaturePrivateKeyLocation.localKeypair,
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
