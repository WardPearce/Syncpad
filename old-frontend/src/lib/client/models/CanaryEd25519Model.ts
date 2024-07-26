/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CanaryEd25519Model = {
    /**
     * ed25519 public key, base64 encoded
     */
    public_key: string;
    /**
     * IV for cipher text, base64 encoded.
     */
    iv: string;
    /**
     * ed25519 private key, encrypted with keychain, base64 encoded
     */
    cipher_text: string;
};

