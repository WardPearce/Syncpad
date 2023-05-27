import sodium from "libsodium-wrappers-sumo";
import { navigate } from 'svelte-navigator';
import { type CanaryModel } from './client/models/CanaryModel';
import { hashBase64Encode } from './crypto/hash';
import secretKey, { SecretkeyLocation } from './crypto/secretKey';


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

export default {
  goToCanary
};
